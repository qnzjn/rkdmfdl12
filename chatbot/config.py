import os
from dotenv import load_dotenv

# .env 파일 로드 시도
load_dotenv()

# API 키 설정 (하드코딩된 키 사용)
GEMINI_API_KEY = "AIzaSyCDiR4YDjYGyS44jwjfiXqSZVfFtVLjQ5U"

# 봇 이름 설정
BOT_NAME = "GeminiBot"

# 욕설/비난 단어 목록 확장
HARMFUL_WORDS = [
    "바보", "멍청이", "죽어", "꺼져", "나쁜", "싫어", "미워",
    "씨발", "병신", "새끼", "지랄", "개새끼", "미친",
    "놈", "년", "악마", "등신", "멍충이", "죽을래",
    "못생긴", "바보야", "멍청아", "white", "black",
    # 필요한 욕설/비난 단어 추가 가능
]

# 경고 메시지 수정
WARNING_MESSAGE = "🚫 부적절한 언어 사용이 감지되었습니다.\n서로를 배려하는 채팅 문화를 만들어주세요."

# API 키 유효성 검사 함수
def is_api_key_valid():
    return GEMINI_API_KEY is not None and len(GEMINI_API_KEY) > 0
