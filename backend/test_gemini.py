from dotenv import load_dotenv; load_dotenv()
import os, httpx

api_key = os.getenv("GEMINI_API_KEY", "")
print(f"API Key: {'YES (' + api_key[:10] + '...)' if api_key else 'MISSING'}\n")

models = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-pro"]

for model_name in models:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": "Say hello in one sentence."}]}]
    }
    try:
        with httpx.Client(timeout=30.0) as client:
            r = client.post(url, json=payload)
        if r.status_code == 200:
            text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
            print(f"SUCCESS [{model_name}]: {text.strip()[:100]}")
            break
        else:
            print(f"FAILED [{model_name}]: HTTP {r.status_code} - {r.text[:120]}")
    except Exception as e:
        print(f"ERROR [{model_name}]: {e}")
