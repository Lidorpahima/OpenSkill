
import requests
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .. import database, models
from fastapi import Depends

router = APIRouter()

AI_API_URL = "https://open-ai251.p.rapidapi.com/ask"
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "c2fbf89f7fmshdbb0fc4609d3d0dp176c13jsn5cfacb2cead9")

class ChatMessage(BaseModel):
    user_id: int
    message: str

@router.post("/chat/")
async def chat_with_ai(chat: ChatMessage, db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(select(models.ChatSession).filter(models.ChatSession.user_id == chat.user_id))
    chat_history = result.scalars().all()

    history_text = "You are an AI career assistant. The user is a complete beginner and does not know about professions. Guide them step by step like a child.\n"
    for entry in chat_history:
        history_text += f"User: {entry.message}\nAI: {entry.response}\n"

    prompt = (
        f"{history_text}\n"
        "Ask the user a **simple and beginner-friendly question** to understand their interests. Example:\n"
        "- What do you enjoy doing in your free time?\n"
        "- Do you like solving puzzles or making things?\n"
        "- Do you enjoy working with computers, people, or something else?\n"
        "If the user gives an unclear answer, kindly rephrase and ask again.\n"
        "Your answer should be only the next question, nothing else."
        f"\n\nUser: {chat.message}\nAI:"
    )

    response = requests.post(
        AI_API_URL, 
        json={"query": prompt}, 
        headers = {
			"x-rapidapi-key": RAPIDAPI_KEY,
			"x-rapidapi-host": "open-ai251.p.rapidapi.com",
			"Content-Type": "application/json",
			"X-RapidAPI-Key": "4fb84e5862msh93493191641aa67p1730ebjsn9a38755eabe6",
			"X-RapidAPI-Host": "open-ai25.p.rapidapi.com"
		}
    )

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to communicate with AI")

    ai_response = response.json().get("response", "No response")

    db_chat = models.ChatSession(user_id=chat.user_id, message=chat.message, response=ai_response)
    db.add(db_chat)
    await db.commit()

    if len(chat_history)>= 4:

        updated_chat_history = chat_history + [models.ChatSession(user_id=chat.user_id, message=chat.message, response=ai_response)]
        recommended_goal = await recommend_learning_path(chat.user_id, updated_chat_history, db)
        return {"response": ai_response, "recommendation": recommended_goal}

    return {"response": ai_response}

async def recommend_learning_path(user_id: int, chat_history, db: AsyncSession):
    messages = "\n".join([f"User: {entry.message}\nAI: {entry.response}" for entry in chat_history])

    summary_prompt = (
        "You are an AI assistant helping a beginner choose a career. The user does not know much about professions, "
        "so you must explain your recommendation in **very simple words**.\n"
        "The user has already answered 5 questions, so **do not** ask more questions.\n"
        "Now, based on the conversation history below, **you must choose a career** and explain why it fits the user.\n"
        "Only return the response in JSON format:\n"
        "{\n  \"title\": \"<Career Name>\",\n  \"description\": \"<Explain in a very simple way why this career fits>\"\n}\n"
        "Do **not** add any extra text. Do **not** ask any more questions. Just return a valid JSON object."
        "\n\nConversation history:\n"
        f"{messages}\n"
    )
    response = requests.post(
        AI_API_URL, 
        json={"query": summary_prompt}, 
        headers = {
			"x-rapidapi-key": RAPIDAPI_KEY,
			"x-rapidapi-host": "open-ai251.p.rapidapi.com",
			"Content-Type": "application/json",
			"X-RapidAPI-Key": "4fb84e5862msh93493191641aa67p1730ebjsn9a38755eabe6",
			"X-RapidAPI-Host": "open-ai25.p.rapidapi.com"
		}
    )

    if response.status_code != 200:
        return "Failed to generate recommendation."

    try:
        recommended_goal = response.json()
        title = recommended_goal.get("title", "No title")
        description = recommended_goal.get("description", "No description")
    except:
        return {"title": "Unknown", "description": "AI response was not in the expected format."}

    return {
        "title": title,
        "description": description
    }