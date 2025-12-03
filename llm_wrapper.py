# llm_wrapper.py
import os
import requests
import json

LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'none').lower()
API_KEY = os.getenv('LLM_API_KEY', '')

def generate_explanation(prompt, max_tokens=200):
    """
    Returns a short explanation text for a recommended career.
    Implement provider functions below (Gemini, OpenAI, etc.) and call them here.
    """
    if LLM_PROVIDER == 'openai':
        return generate_with_openai(prompt, max_tokens)
    elif LLM_PROVIDER == 'gemini':
        return generate_with_gemini(prompt, max_tokens)
    else:
        # Fallback: simple templated explanation
        return "Explanation: " + (prompt[:400] + '...')

def generate_with_openai(prompt, max_tokens=200):
    try:
        import openai
        openai.api_key = API_KEY
        resp = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=0.7,
            n=1
        )
        return resp.choices[0].text.strip()
    except Exception as e:
        return f"[OpenAI error] {e}"

def generate_with_gemini(prompt, max_tokens=200):
    """
    Placeholder for Gemini call.
    Gemini's exact integration depends on the client / SDK you use (Google Generative AI SDK or REST).
    Replace the contents of this function with the appropriate Gemini client call, for example:

    - using google-generative-ai Python client:
        from google.generativeai import Client
        client = Client(api_key=API_KEY)
        res = client.generate_text(model="gemini-1.0", prompt=prompt)
        return res.text

    - or using HTTP requests to your Gemini endpoint (if available).

    For now this returns a placeholder so the app works offline.
    """
    return "LLM placeholder explanation for: " + (prompt[:300] + '...')
