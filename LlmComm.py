import json, requests
from dotenv import load_dotenv
import os
from google import genai
import re 

load_dotenv()
def strip_code_fences(text):
    return re.sub(r"^```[a-zA-Z]*\s*|\s*```$", "", text.strip())


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
    return strip_code_fences(response["choices"][0]["message"]["content"].strip())

if __name__=="__main__":
    print(askLlm("What is the meaning of life"," "))