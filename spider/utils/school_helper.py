from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Replace hardcoded endpoint with environment variable
api_endpoint = os.getenv('OLLAMA_API_ENDPOINT', 'http://localhost:11435/v1/chat/completions')

def get_school_abbreviation(url: str) -> str:
    """
    Get school name abbreviation by sending request to AI service
    
    Args:
        url (str): URL of the school's website
        
    Returns:
        str: Abbreviated school name or empty string if request fails
    """
    try:

        payload = {
            "model": "llama3.2",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": "請根據以下網址，輸出網址中的縮寫校名：https://politics.ntu.edu.tw/:f{url}"
                }
            ],
            "temperature": 0.01,
            "top_p": 1.0,
            "max_tokens": 1000,
        }
    
        response = requests.post(api_endpoint, json=payload)
        
        if response.status_code == 500:
            print(f"Server error response: {response.text}")
            return "server error"
            
        response.raise_for_status()
        result = response.json()

        print(result)

        return result["choices"][0]["message"]["content"].strip()
        
    except requests.RequestException as e:
        print(f"Error getting school abbreviation: {e}")
        return "" 