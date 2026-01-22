import json, requests
from dotenv import load_dotenv
import os

load_dotenv()

def askLlm(prompt:str, model:str, max_token:int = 800, temperature:int =0.0):
    LLM_API_KEY=os.getenv("LLM_API_KEY")
    response = requests.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json",
    },
    json={
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "Do not include reasoning or analysis. Only output the final answer."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": max_token,
        "temperature": temperature
    }
    )
    response=response.json()
    return response["choices"][0]["message"]["content"].strip()