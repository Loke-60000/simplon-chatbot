import os

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware

from openai import AzureOpenAI

from functions.webbrowsingllm import find_url, extract_content_from_urls, perform_content_search

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = os.getenv("AZURE_OPENAI_KEY")
if not api_key:
    raise Exception("API key not found")
client = AzureOpenAI(
    azure_endpoint="https://openai-lok.openai.azure.com/",
    api_key=api_key,
    api_version="2024-02-15-preview"
)


class Message(BaseModel):
    sender: str
    message: str


class ChatRequest(BaseModel):
    system: str = "You are an ai assistant with a browser provide the user with data when you get informations from a website"
    history: List[Message]
    temperature: float = 0.9
    max_tokens: int = 1000
    top_p: float = 0.95
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0


@app.post("/generate-text", response_model=dict)
async def generate_text(request: ChatRequest):
    last_user_message = request.history[-1].message if request.history else ""
    urls = find_url(last_user_message)

    response_text = extract_content_from_urls(urls) if urls else ""

    search_keywords = ["search", "look for", "find", "online", "web"]
    if not response_text and any(keyword in last_user_message.lower() for keyword in search_keywords):
        search_query = last_user_message.split(next(
            keyword for keyword in search_keywords if keyword in last_user_message.lower()), 1)[1].strip()
        response_text = perform_content_search(search_query)

    if not response_text:
        response_text = "Please provide a URL or specify a search query."

    system_message = f"Here's what I found based on your request: {response_text}"
    request.history.append(Message(sender="system", message=system_message))

    messages = [{"role": "system" if msg.sender == "system" else "user",
                 "content": msg.message} for msg in request.history]

    try:
        completion = client.chat.completions.create(
            model="gpt35-latest",
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            top_p=request.top_p,
            frequency_penalty=request.frequency_penalty,
            presence_penalty=request.presence_penalty
        )
        completion_dict = completion.model_dump()
        choices = completion_dict.get('choices', [])
        if choices:
            first_choice = choices[0]
            generated_text = first_choice.get('message', {}).get(
                'content', 'No content available')
            response_data = {
                "response": generated_text,
                "config": {
                    "temperature": request.temperature,
                    "max_tokens": request.max_tokens,
                    "top_p": request.top_p,
                    "frequency_penalty": request.frequency_penalty,
                    "presence_penalty": request.presence_penalty
                },
                "system_message": system_message,
            }
            return JSONResponse(content=response_data)
        else:
            return JSONResponse(content={"error": "No choices available"}, status_code=500)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
