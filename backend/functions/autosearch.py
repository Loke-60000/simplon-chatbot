import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from openai import AzureOpenAI


class AzureOpenAIService:
    def __init__(self, api_key, endpoint, version):
        if not api_key:
            raise ValueError("API key is required")
        self.client = AzureOpenAI(
            azure_endpoint=endpoint, api_key=api_key, api_version=version)

    def generate_chat_completion(self, messages, temperature, max_tokens, top_p, frequency_penalty, presence_penalty):
        try:
            completion = self.client.chat.completions.create(
                model="gpt35-latest",
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty
            )
            if completion.choices:
                choice = completion.choices[0]
                return choice.message.content if choice.message.content else 'No content available'
            else:
                return 'No choices available'
        except Exception as e:
            print(f"Error during AI completion: {str(e)}")
            return None


def setup_webdriver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.binary_location = '/usr/bin/chromium'
    service = Service(executable_path='/usr/bin/chromedriver')
    return webdriver.Chrome(service=service, options=chrome_options)


def perform_search(driver, query):
    print(f"Performing search for: {query} at {datetime.now()}")
    search_url = f"https://www.google.com/search?q={query}"
    driver.get(search_url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div#search")))
    results = driver.find_elements(By.CSS_SELECTOR, 'div.g')
    links = [result.find_element(By.CSS_SELECTOR, 'a').get_attribute(
        'href') for result in results]
    return links


def scrape_and_extract_text(driver, url):
    print(f"Scraping URL: {url} at {datetime.now()}")
    driver.get(url)
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "body")))
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    text_content = ' '.join(p.get_text(strip=True) for p in soup.find_all('p'))
    return text_content


def intelligent_search(initial_query, azure_ai_service):
    driver = setup_webdriver()
    try:
        query = initial_query
        max_attempts = 5
        current_attempt = 0
        while current_attempt < max_attempts:
            links = perform_search(driver, query)
            for link in links:
                content = scrape_and_extract_text(driver, link)
                if "desired information" in content:
                    print("Relevant information found:", content)
                    return content
                messages = [{'role': 'system', 'content': 'Refine the search query based on the content.'},
                            {'role': 'user', 'content': content}]
                new_query = azure_ai_service.generate_chat_completion(
                    messages, 0.7, 100, 1, 0.5, 0.5)
                if new_query:
                    query = new_query
                    print("Refining search with new query:", query)
                    break
            current_attempt += 1
        print("Relevant information not found.")
    finally:
        driver.quit()




api_key = os.getenv("AZURE_OPENAI_KEY")
if not api_key:
    raise Exception("API key not found")

endpoint = "https://openai-lok.openai.azure.com/"
version = "2024-02-15-preview"
azure_ai_service = AzureOpenAIService(api_key, endpoint, version)

sintelligent_search("Who owns the rights to Steins;Gate?", azure_ai_service)
