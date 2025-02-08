import os
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .. import database, models
from .chat_request import ask_gpt
from .schemas import ChatMessage, ChatResponse, CareerRecommendation
from ..database import redis_client  
from .models import UserCareerChoice
import requests
import random


router = APIRouter()

MAX_HISTORY_MESSAGES = 5 

system_message = (
    "You are an AI career assistant. Guide the user step by step.\n"
    "Keep answers short. Confirm their response in 1 sentence.\n"
    "Then, ask exactly **one** follow-up question.\n"
    "Avoid details. Do not ask multiple questions."
)

@router.post("/chat/")
async def chat_with_ai(chat: ChatMessage, db: AsyncSession = Depends(database.get_db)):
    user_id = chat.user_id
    await check_user_exists(user_id)

    user_key = f"chat_history:{user_id}"
    chat_history = redis_client.lrange(user_key, -MAX_HISTORY_MESSAGES * 2, -1)

    history_text = f"System: {system_message}\n"
    for i in range(0, len(chat_history), 2):
        history_text += f"User: {chat_history[i]}\nAI: {chat_history[i + 1]}\n"

    prompt = f"{history_text}\nUser: {chat.message}\nAI:"

    ai_response = ask_gpt(prompt, max_input_length=300)

    redis_client.rpush(user_key, chat.message, ai_response)
    redis_client.ltrim(user_key, -MAX_HISTORY_MESSAGES * 2, -1)

    recommendation = None
    print(f"🔍 DEBUG: chat_history length → {len(chat_history)}")  # בודק האם באמת יש 5 תשובות

    if len(chat_history) >= (MAX_HISTORY_MESSAGES - 1) * 2:
        recommended_careers = await recommend_learning_path(user_id, chat_history, db)
        print(f"🔍 DEBUG: Recommended Careers → {recommended_careers}")  # בודק שהתשובה תקינה
        recommendation = [CareerRecommendation(**career) for career in recommended_careers]
        return 
        
    return ChatResponse(response=ai_response, recommendation=recommendation)


import json

async def recommend_learning_path(user_id: int, chat_history, db: AsyncSession):
    messages = "\n".join([f"User: {chat_history[i]}\nAI: {chat_history[i + 1]}" for i in range(0, len(chat_history), 2)])
    
    summary_prompt = (
        "STOP ASKING QUESTIONS. IT'S TIME TO CHOOSE A CAREER.\n"
        "You **must** return exactly 3 career options, no more, no less.\n"
        "Each career should have:\n"
        "- `title`: A 2-3 word career name.\n"
        "- `description`: A **VERY SHORT** reason (max 8 words).\n"
        "- `match_percentage`: A number between 50 and 100.\n"
        "Return **only** this JSON format, no explanations:\n"
        "[\n"
        "  { \"title\": \"Career 1\", \"description\": \"Short reason\", \"match_percentage\": 85 },\n"
        "  { \"title\": \"Career 2\", \"description\": \"Short reason\", \"match_percentage\": 75 },\n"
        "  { \"title\": \"Career 3\", \"description\": \"Short reason\", \"match_percentage\": 60 }\n"
        "]\n"
        "Do **not** add any text before or after the JSON.\n"
        "**Your answer must be a complete valid JSON array in one response. Do NOT split the response.**"
    )

    try:
        ai_response = ask_gpt(summary_prompt, max_input_length=1000)
        print(f"🔍 DEBUG: AI Raw Response → {ai_response}")  # Debugging

        # ניקוי תשובה - הסרת ` ```json ` אם קיים
        cleaned_response = ai_response.strip().strip("```json").strip("```").strip()

        # בדיקה אם ה-JSON קטוע, ננסה לתקן
        if not cleaned_response.endswith("]"):
            print("⚠️ WARNING: AI response seems to be incomplete. Attempting to fix...")
            cleaned_response += "]"  # הוספת סוגר חסר

        # ניסיון לטעון את ה-JSON
        recommended_careers = json.loads(cleaned_response)

        # בדיקה האם קיבלנו 3 קריירות, אם לא - נבקש שוב
        if not isinstance(recommended_careers, list) or len(recommended_careers) != 3:
            raise ValueError("AI response is not a valid list of 3 careers.")

        save_recommendations_to_redis(user_id, recommended_careers)
        return recommended_careers

    except (json.JSONDecodeError, ValueError) as e:
        print(f"❌ ERROR: Invalid AI response format → {str(e)}")

        # אם ה-AI החזיר תשובה ריקה או לא תקינה, נבקש תיקון
        print("⚠️ WARNING: AI response was invalid. Requesting clarification...")
        clarification_prompt = (
            "Your last response was empty or incomplete. Please return the full JSON response again.\n"
            "Do **not** add any extra text. Just return the valid JSON array."
        )

        ai_response = ask_gpt(clarification_prompt, max_input_length=500)
        cleaned_response = ai_response.strip().strip("```json").strip("```").strip()

        try:
            recommended_careers = json.loads(cleaned_response)

            if not isinstance(recommended_careers, list) or len(recommended_careers) != 3:
                raise ValueError("AI response is not a valid list of 3 careers.")

            save_recommendations_to_redis(user_id, recommended_careers)
            return recommended_careers
        except (json.JSONDecodeError, ValueError) as e:
            print(f"❌ ERROR: Clarification request also failed → {str(e)}")
            return [
                {
                    "title": "Unknown",
                    "description": "AI response was not in the expected format.",
                    "match_percentage": 0
                }
            ]



@router.post("/chat/select_career/")
async def select_career(user_id: int, career_id: int, db: AsyncSession = Depends(database.get_db)):
    cached_recommendations = redis_client.get(f"career_recommendations:{user_id}")

    if not cached_recommendations:
        raise HTTPException(status_code=404, detail="No career recommendations found. Try answering more questions.")

    recommended_careers = json.loads(cached_recommendations)

    selected_career = next((career for career in recommended_careers if career["id"] == career_id), None)

    if not selected_career:
        raise HTTPException(status_code=400, detail="Invalid career choice.")

    db_career = UserCareerChoice(
        user_id=user_id,
        title=selected_career["title"],
        description=selected_career["description"]
    )
    db.add(db_career)
    await db.commit()

    redis_client.delete(f"career_recommendations:{user_id}")
    return {"message": f"Career '{selected_career['title']}' saved successfully!", "career": selected_career}


def save_recommendations_to_redis(user_id, recommended_careers):
    for i, career in enumerate(recommended_careers, start=1):
        career["id"] = i  

    redis_client.set(f"career_recommendations:{user_id}", json.dumps(recommended_careers))


USER_SERVICE_URL = "http://user_service:8000"  

async def check_user_exists(user_id: int):
    response = requests.get(f"{USER_SERVICE_URL}/users/{user_id}")

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="User does not exist")

    return response.json()  # מחזיר את נתוני המשתמש