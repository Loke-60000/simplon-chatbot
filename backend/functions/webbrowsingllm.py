from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from openai import AzureOpenAI

import re

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.binary_location = '/usr/bin/chromium'
service = Service(executable_path='/usr/bin/chromedriver')


class AzureOpenAIService:
    def __init__(self, api_key, endpoint, version):
        if not api_key:
            raise ValueError("API key is required")
        self.client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=version
        )

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
            completion_dict = completion.model_dump()
            choices = completion_dict.get('choices', [])
            if choices:
                return choices[0].get('message', {}).get('content', 'No content available')
        except Exception as e:
            raise Exception(str(e))



def setup_webdriver():
    return webdriver.Chrome(service=service, options=chrome_options)


def find_url(text):
    url_pattern = r"\b(https?://)?([a-z0-9-]+(\.[a-z0-9-]+)+)(:\d+)?(/[^\s]*)?\b"
    urls = re.findall(url_pattern, text)
    full_urls = []
    for parts in urls:
        scheme, domain, _, port, path = parts
        if not scheme:
            scheme = 'http://'
        full_url = f"{scheme}{domain}{port if port else ''}{path if path else ''}"
        full_urls.append(full_url)
    return full_urls


def scrape_site(url):
    try:
        driver = setup_webdriver()
        driver.get(url)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body")))
        html = driver.page_source
        driver.quit()
        soup = BeautifulSoup(html, 'html.parser')
        return soup
    except Exception as e:
        print(f"Error occurred while scraping {url}: {str(e)}")
        return None


def extract_text_content(soup):
    text_content = {
        'titles': [soup.title.get_text(strip=True)] if soup.title else [],
        'headings': [tag.get_text(strip=True) for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])],
        'paragraphs': [p.get_text(strip=True) for p in soup.find_all('p')],
        'lists': [li.get_text(strip=True) for li in soup.find_all('li') if li.get_text(strip=True)],
        'tables': [table.get_text(strip=True) for table in soup.find_all('table') if table.get_text(strip=True)],
    }
    return text_content


def perform_search(query):
    driver = setup_webdriver()
    search_url = f"https://www.google.com/search?q={query}"
    driver.get(search_url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div#search")))
    results = driver.find_elements(By.CSS_SELECTOR, 'div.g')
    links = [result.find_element(By.CSS_SELECTOR, 'a').get_attribute(
        'href') for result in results if result.find_element(By.CSS_SELECTOR, 'a')]
    driver.quit()
    return links


async def generate_refined_query(prompt):
    try:
        completion = client.chat.completions.create(
            model="gpt35-latest",
            messages=[{"role": "system", "content": prompt}],
            temperature=0.5,
            max_tokens=100
        )
        return completion.choices[0].text.strip()
    except Exception as e:
        print(f"Error: {str(e)}")
        return None


async def refine_search(query):
    print(f"Refining search for: {query}")
    links = perform_search(query)
    for link in links:
        soup = scrape_site(link)
        if soup:
            text_content = extract_text_content(soup)
            prompt = f"Based on the following content, refine the search query: {text_content['titles']} {text_content['paragraphs']}"
            refined_query = await generate_refined_query(prompt)
            if 'desired condition' in refined_query:
                return link
    return None


def extract_content_from_urls(urls):
    """ Extract content from the list of URLs """
    content = ""
    for url in urls:
        soup = scrape_site(url)
        if soup:
            page_content = extract_text_content(soup)
            content += f"\nExtracted from {url}: {page_content['titles'] + page_content['headings']} + {page_content['paragraphs']} + {page_content['lists']}"
    return content


def perform_content_search(query):
    """ Perform a web search and extract content from the top links """
    content = ""
    links = perform_search(query)
    for link in links[:3]:  # Limit top 3 links
        soup = scrape_site(link)
        if soup:
            page_content = extract_text_content(soup)
            content += f"\nFrom {link}: {page_content['titles']} {page_content['headings']} {page_content['paragraphs']}"
    return content
