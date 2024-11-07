import os
from dotenv import load_dotenv

# .env 파일이 없어도 실행되도록 수정
try:
    load_dotenv()
except:
    pass

# 기본값 설정
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', "your_api_key_here")
BOT_NAME = "GeminiBot"
