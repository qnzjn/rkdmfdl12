import os
from dotenv import load_dotenv

# .env 파일 로드 시도
load_dotenv()

# API 키 설정 (하드코딩된 키 사용)
GEMINI_API_KEY = "AIzaSyCDiR4YDjYGyS44jwjfiXqSZVfFtVLjQ5U"

# 봇 이름 설정
BOT_NAME = "GeminiBot"

# API 키 유효성 검사 함수
def is_api_key_valid():
    return GEMINI_API_KEY is not None and len(GEMINI_API_KEY) > 0
