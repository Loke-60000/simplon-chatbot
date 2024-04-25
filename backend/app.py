import os
from typing import List

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from openai import AzureOpenAI

from fastapi.middleware.cors import CORSMiddleware

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
    system: str
    history: List[Message]
    temperature: float = 0.9
    max_tokens: int = 1000
    top_p: float = 0.95
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0


@app.post("/generate-text", response_model=dict)
async def generate_text(request: ChatRequest):
    message_text = [
        {"role": "system", "content": request.system} if msg.sender == "system" else {"role": "user", "content": msg.message} for msg in request.history
    ]

    try:
        completion = client.chat.completions.create(
            model="gpt35-latest",
            messages=message_text,
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
                }
            }
            return JSONResponse(content=response_data)
        else:
            return JSONResponse(content={"error": "No choices available"}, status_code=500)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
