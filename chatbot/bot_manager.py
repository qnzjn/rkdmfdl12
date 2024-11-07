import google.generativeai as genai
from datetime import datetime
from .config import GEMINI_API_KEY, BOT_NAME, is_api_key_valid, HARMFUL_WORDS, WARNING_MESSAGE

class BotManager:
    def __init__(self):
        self.is_enabled = False
        if is_api_key_valid():
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                self.model = genai.GenerativeModel('gemini-pro')
                self.chat = self.model.start_chat(history=[])
                self.welcomed_users = set()
                self.warning_counts = {}  # 사용자별 경고 횟수
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
            "content": f"👋 안녕하세요! {username}님! 저는 {BOT_NAME}입니다. 즐거운 채팅 되세요! (욕설/비난 감지 기능이 활성화되어 있습니다)",
            "username": BOT_NAME,
            "time": datetime.now().strftime("%H:%M")
        }

    def check_harmful_content(self, message):
        """욕설/비난 감지 - 대소문자 구분 없이 검사"""
        message = message.lower()  # 소문자로 변환
        found_words = []
        for word in HARMFUL_WORDS:
            if word.lower() in message:  # 소문자로 변환하여 비교
                found_words.append(word)
        return found_words

    def process_message(self, message, username):
        """메시지 처리 및 욕설/비난 감지"""
        if not self.is_enabled:
            return None

        # 욕설/비난 감지
        harmful_words = self.check_harmful_content(message)
        if harmful_words:
            # 경고 횟수 증가
            self.warning_counts[username] = self.warning_counts.get(username, 0) + 1
            count = self.warning_counts[username]
            
            # 경고 메시지 생성
            warning = f"🚫 [{username}님께 드리는 {count}번째 경고] {WARNING_MESSAGE}\n"
            warning += f"⚠️ 감지된 부적절한 단어: {', '.join(harmful_words)}\n"
            
            if count >= 3:
                warning += "\n❗️경고: 3회 이상 부적절한 언어를 사용하셨습니다. 계속되는 경우 제재 조치될 수 있습니다."
            
            return {
                "role": "assistant",
                "content": warning,
                "username": BOT_NAME,
                "time": datetime.now().strftime("%H:%M")
            }
            
        return None
