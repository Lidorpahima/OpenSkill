import openai 
import os
from dotenv import load_dotenv
import tiktoken
from openai import OpenAIError

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def num_tokens_from_string(string, model="gpt-4o-mini"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(string))

#Method to ask GPT-4o mini a question
def ask_gpt(message, model="gpt-4o-mini", max_tokens=50, max_input_length=100):
    tokenCount = num_tokens_from_string(message, model)
    if num_tokens_from_string(message, model) > max_input_length:
        return f"⚠️ Please keep your answer under {max_input_length} words.(Used {tokenCount}) ⚠️"
    try:
        print("Token count: ", tokenCount)
        openai.api_key = os.getenv("OPENAI_API_KEY")
        client = openai.OpenAI(api_key=openai.api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": message}],
            max_tokens=max_tokens
        )
        return response.choices[0].message.content

    except OpenAIError as e:
        return f"❌ Error: {str(e)} ❌"