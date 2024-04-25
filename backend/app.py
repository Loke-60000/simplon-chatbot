import os

from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from openai import AzureOpenAI
from pydantic import BaseModel
from typing import List

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chrome_options = Options()
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.binary_location = '/usr/bin/chromium-browser'

service = Service(executable_path='/usr/bin/chromedriver')

driver = webdriver.Chrome(service=service, options=chrome_options)


def scrape_site(url):
    """
    Scrape a website using Selenium and return a BeautifulSoup object.
    """
    try:
        with webdriver.Chrome(service=service, options=chrome_options) as driver:
            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body")))
            html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        return soup
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return None


def extract_text_content(soup):
    """
    Extracts and returns notable text-holding elements from a webpage.

    """
    text_content = {
        'titles': [],
        'headings': [],
        'paragraphs': [],
        'lists': []
    }

    if soup.title:
        text_content['titles'].append(soup.title.get_text(strip=True))

    for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        text_content['headings'].append(tag.get_text(strip=True))

    for paragraph in soup.find_all('p'):
        text_content['paragraphs'].append(paragraph.get_text(strip=True))

    for li in soup.find_all('li'):
        text = li.get_text(strip=True)
        if text:
            text_content['lists'].append(text)

    return text_content


url = "https://lokman.fr"
page_content = str(extract_text_content(scrape_site(url)))

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
    system: str = f'You are an helpful AI, these are the informations you have about Lokman: {page_content}'
    history: List[Message]
    temperature: float = 0.9
    max_tokens: int = 1000
    top_p: float = 0.95
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0



@app.post("/generate-text", response_model=dict)
async def generate_text(request: ChatRequest):
    print(page_content)
    print(request.history)
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
