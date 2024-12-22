from dotenv import load_dotenv
import os
from bot import UniversityAdmissionBot

def main():
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    
    if api_key is None:
        print("Error: OPENAI_API_KEY is not set.")
        return
    else:
        print("API key loaded successfully.")
    
    # Create output directory if it doesn't exist
    os.makedirs('data/output', exist_ok=True)
    
    bot = UniversityAdmissionBot(api_key)
    
    # Get user input
    country = input("請輸入國家：")
    university = input("請輸入大學名稱：")
    degree = input("請輸入欲申請的學位：")
    major = input("請輸入系所：")
    
    print("\n正在查詢入學資訊，請稍候...")
    # Get information
    result = bot.get_admission_info(country, university, degree, major)
    
    # Display the result
    print("\n查詢結果：")
    print("-" * 50)  # Separator line
    for key, value in result.items():
        print(f"{key}: {value}")
    print("-" * 50)  # Separator line
    
    print("\n結果已儲存為 CSV 檔案")

if __name__ == "__main__":
    main() 