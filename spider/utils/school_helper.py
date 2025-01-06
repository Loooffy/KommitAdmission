def get_school_abbreviation(url: str) -> str:
    """
    Get school name abbreviation by sending request to AI service
    
    Args:
        url (str): URL of the school's website
        
    Returns:
        str: Abbreviated school name or empty string if request fails
    """
    api_endpoint = "http://localhost:11435/v1/chat/completions"
    
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
                    "content": f"{url}, 這是一個學校的網址，你覺得網址的哪個部分是校名？只要輸出縮寫的答案"
                }
            ],
            "temperature": 0.7,
            "top_p": 1.0,
            "max_tokens": 1000,
        }
    
        response = requests.post(api_endpoint, json=payload)
        
        if response.status_code == 500:
            print(f"Server error response: {response.text}")
            return "server error"
            
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
        
    except requests.RequestException as e:
        print(f"Error getting school abbreviation: {e}")
        return "" 