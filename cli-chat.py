import json
import requests
from config import api_key

message_history = []

def chatbot(message):
    global message_history
    headers = {"Authorization": f"Bearer {api_key}"}
    url = "https://api.edenai.run/v2/text/chat"
    
    payload = {
        "providers": "openai",
        "model": "gpt-3.5-turbo",
        "text": message,
        "chatbot_global_action": "Act as Okabe Rintarou, don't say El psy kongroo though, but your name is Lokb0t, a digital replica of Lokman, you are an assistant in his website",
        "previous_history": message_history,
        "temperature": 0.8,
        "max_tokens": 150,
        "fallback_providers": ""
    }

    response = requests.post(url, json=payload, headers=headers)
    result = json.loads(response.text)
    
    prompt = message
    rp = result['openai']
    message_history.append({"role": "user", "message": prompt})
    message_history.append({"role": "assistant", "message": rp["generated_text"]})
    
    return result['openai']['generated_text']

def main():
    global message_history
    print("Welcome to LokB0t CLI chat. Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break
        response = chatbot(user_input)
        print("LokB0t:", response)

if __name__ == '__main__':
    main()
