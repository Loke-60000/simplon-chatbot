import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import requests
from bs4 import BeautifulSoup
from typing import Optional

from config import api_key, provider, model

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def scrape_text_from_url(url: str) -> str:
    """Scrape and return all text from the given URL."""
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        texts = soup.stripped_strings
        return " ".join(texts)
    else:
        return "Failed to retrieve content from URL."


@app.post("/chat")
def chat(message: Optional[str] = None):
    user_message = message if message else ''
    scraped_text = scrape_text_from_url(
        'http://127.0.0.1:8001/website/index.html')

    ai_context = "As a digital replica of Lokman, named Lokb0t, you have access to information on the website of the church you're working for. Here's some information you know: " + scraped_text
    ai_message = user_message + \
        " [The information above is from the website you're assisting with.]"

    headers = {"Authorization": f"Bearer {api_key}"}
    url = "https://api.edenai.run/v2/text/chat"

    payload = {
        "providers": provider,
        "model": model,
        "text": ai_message,
        "chatbot_global_action": ai_context,
        "temperature": 0.8,
        "max_tokens": 150,
        "fallback_providers": ""
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        result = response.json()
        return JSONResponse(content={"response": result['openai']['generated_text']})
    else:
        return JSONResponse(content={"error": "Failed to get response from the API"}, status_code=500)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
