import os
import requests

from dotenv import load_dotenv
load_dotenv()


API_KEY = os.getenv("GEMINI_API_KEY")

def get_ai_recommendation(prompt):
    if not API_KEY:
        return "API key missing. Add GEMINI_API_KEY to your .env"

    url = (
        "https://generativeai.googleapis.com/v1beta/models/gemini-1.5:generateContent"

        f"?key={API_KEY}"
    )

    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }

    try:
        response = requests.post(url, json=payload)

        if response.status_code != 200:
            return f"Error {response.status_code}: {response.text}"

        data = response.json()

        return data["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as e:
        return f"Exception: {e}"
