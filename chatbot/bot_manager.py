import google.generativeai as genai
from datetime import datetime
from .config import GEMINI_API_KEY, BOT_NAME

class BotManager:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        self.chat = self.model.start_chat(history=[])
        self.welcomed_users = set()  # 인사한 사용자 추적

    def get_welcome_message(self, username):
        # 이미 인사한 사용자면 None 반환
        if username in self.welcomed_users:
            return None
            
        # 인사한 사용자 기록
        self.welcomed_users.add(username)
        
        return {
            "role": "assistant",
            "content": f"👋 안녕하세요! {username}님! 즐거운 채팅 되세요!",
            "username": BOT_NAME,
            "time": datetime.now().strftime("%H:%M")
        }

    def process_message(self, message):
        # 인사 후에는 더 이상 응답하지 않음
        return None
