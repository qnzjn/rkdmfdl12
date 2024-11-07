import google.generativeai as genai
from datetime import datetime
from .config import GEMINI_API_KEY, BOT_NAME, is_api_key_valid

class BotManager:
    def __init__(self):
        self.is_enabled = False
        if is_api_key_valid():
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                self.model = genai.GenerativeModel('gemini-pro')
                self.chat = self.model.start_chat(history=[])
                self.welcomed_users = set()
                self.is_enabled = True
            except Exception as e:
                print(f"Bot initialization error: {str(e)}")
                self.is_enabled = False

    def get_welcome_message(self, username):
        if not self.is_enabled:
            return None
            
        if username in self.welcomed_users:
            return None
            
        self.welcomed_users.add(username)
        
        return {
            "role": "assistant",
            "content": f"👋 안녕하세요! {username}님! 저는 {BOT_NAME}입니다. 즐거운 채팅 되세요!",
            "username": BOT_NAME,
            "time": datetime.now().strftime("%H:%M")
        }

    def process_message(self, message):
        return None  # 웰컴 메시지 이후에는 응답하지 않음
