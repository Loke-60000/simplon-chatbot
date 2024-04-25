from openai import AzureOpenAI


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
