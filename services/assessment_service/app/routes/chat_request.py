import os
import requests
import json
from dotenv import load_dotenv
import tiktoken

load_dotenv()
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
URL=os.getenv("MODEL_URL")
MODEL=os.getenv("MODEL")
def ask_gpt(message, model=MODEL):
    try:
        response = requests.post(
            url=URL,
            headers={
                "Authorization": f"Bearer {openrouter_api_key}",
                "Content-Type": "application/json",
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

