import os, httpx
from dotenv import load_dotenv; load_dotenv()
api_key = os.getenv('GEMINI_API_KEY', '')

print(f"Testing API key ending in {api_key[-4:] if api_key else 'NONE'}")
for m in ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-1.5-pro']:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
    try:
        r = httpx.post(url, json={"contents": [{"parts": [{"text": "hi"}]}]})
        print(f"{m}: HTTP {r.status_code}")
        if r.status_code != 200:
            print(f"Error: {r.json().get('error', {}).get('message', r.text)[:150]}")
    except Exception as e:
        print(f"{m}: Network Error {e}")
