import requests

class PerplexityAPI:
    def __init__(self, api_token: str):
        self.url = "https://api.perplexity.ai/chat/completions"
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
    def get_response(self, user_content: str):
        payload = {
            "model": "llama-3.1-sonar-small-128k-online",
            "messages": [
                {
                    "role": "system",
                    "content": "Be precise and concise."
                },
                {
                    "role": "user",
                    "content": user_content
                }
            ],
            "max_tokens": "Optional",
            "temperature": 0.2,
            "top_p": 0.9,
            "search_domain_filter": ["perplexity.ai"],
            "return_images": False,
            "return_related_questions": False,
            "search_recency_filter": "month",
            "top_k": 0,
            "stream": False,
            "presence_penalty": 0,
            "frequency_penalty": 1
        }

        response = requests.request("POST", self.url, json=payload, headers=self.headers)
        return response.text

# Example usage
if __name__ == "__main__":
    api_token = "<your-token-here>"
    perplexity = PerplexityAPI(api_token)
    question = "How many stars are there in our galaxy?"
    result = perplexity.get_response(question)
    print(result)