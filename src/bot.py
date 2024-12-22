from openai import OpenAI
import pandas as pd
from datetime import datetime
import openai

class UniversityAdmissionBot:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        
    def get_admission_info(self, country, university, degree, major):
        print(f"\n開始查詢 {country} {university} {degree} {major} 的入學資訊...")
        
        print("1. 正在查詢基本入學要求...")
        # Get basic requirements
        basic_requirements = self._get_basic_requirements()
        print("基本入學要求查詢完成。")
        
        print("2. 正在查詢語言要求...")
        # Get language requirements
        language_requirements = self._get_language_requirements()
        print("語言要求查詢完成。")
        
        print("3. 正在查詢申請截止日期...")
        # Get application deadlines
        deadlines = self._get_application_deadlines()
        print("申請截止日期查詢完成。")
        
        print("4. 正在查詢所需文件...")
        # Get required documents
        required_documents = self._get_required_documents()
        print("所需文件查詢完成。")
        
        print("5. 正在整理資訊...")
        # Combine all information
        result = {
            "基本入學要求": basic_requirements,
            "語言要求": language_requirements,
            "申請截止日期": deadlines,
            "所需文件": required_documents
        }
        print("資訊整理完成。")
        
        print("資訊查詢完成！\n")
        return result
    
    def _parse_response(self, response):
        # 簡單的回應解析
        lines = response.split('\n')
        info = {
            '申請截止時間': '',
            '申請需要繳交的資料': '',
            '申請條件': '',
            '學費': ''
        }
        
        current_key = ''
        for line in lines:
            line = line.strip()
            if line in info.keys():
                current_key = line
            elif current_key and line:
                info[current_key] = line.replace('：', '')
                
        return info 

    def _get_basic_requirements(self):
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What is the capital of France?"}
            ]
        )
        print(response['choices'][0]['message']['content'])

    pass  # Replace with actual implementation