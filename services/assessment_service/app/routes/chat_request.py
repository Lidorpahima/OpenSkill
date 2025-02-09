import os
import requests
import json
from dotenv import load_dotenv
import tiktoken

# טען את המשתנים מסביבת העבודה
load_dotenv()
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

# Method to ask the model a question
def ask_gpt(message, model="sophosympatheia/rogue-rose-103b-v0.2:free"):
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://your-site-url.com",  # Optional
                "X-Title": "Your Site Name",  # Optional
            },
            data=json.dumps({
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": message
                    }
                ],
            })
        )
        response_data = response.json()
        return response_data['choices'][0]['message']['content']

    except Exception as e:
        return f"❌ Error: {str(e)} ❌"

