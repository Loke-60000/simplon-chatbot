from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

from config import api_key

def scrape_text_from_url(url):
    """Scrape and return all text from the given URL."""
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        texts = soup.stripped_strings
        return " ".join(texts)
    else:
        return "Failed to retrieve content from URL."

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    scraped_text = scrape_text_from_url('http://127.0.0.1:5501/website/index.html')
    
    ai_context = "As a digital replica of Lokman, named Lokb0t, you have access to information on the website of the church you're working for. Here's some information you know: " + scraped_text
    ai_message = user_message + " [The information above is from the website you're assisting with.]"
    
    headers = {"Authorization": f"Bearer {api_key}"}
    url = "https://api.edenai.run/v2/text/chat"
    
    payload = {
        "providers": "openai",
        "model": "gpt-3.5-turbo",
        "text": ai_message,
        "chatbot_global_action": ai_context, 
        "temperature": 0.8,
        "max_tokens": 150,
        "fallback_providers": ""
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        result = response.json()
        return jsonify({"response": result['openai']['generated_text']})
    else:
        return jsonify({"error": "Failed to get response from the API"}), 500

if __name__ == '__main__':
    app.run(debug=True)
