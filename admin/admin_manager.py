import streamlit as st
import json
import os

ADMIN_FILE = "data/admins.json"
BLOCKED_USERS_FILE = "data/blocked_users.json"
FILTERED_WORDS_FILE = "data/filtered_words.json"

class AdminManager:
    def __init__(self):
        self.admins = self.load_admins()
        self.blocked_users = self.load_blocked_users()
        self.filtered_words = self.load_filtered_words()

    def load_admins(self):
        if os.path.exists(ADMIN_FILE):
            with open(ADMIN_FILE, 'r') as f:
                return json.load(f)
        return []

    def load_blocked_users(self):
        if os.path.exists(BLOCKED_USERS_FILE):
            with open(BLOCKED_USERS_FILE, 'r') as f:
                return json.load(f)
        return []

    def load_filtered_words(self):
        if os.path.exists(FILTERED_WORDS_FILE):
            with open(FILTERED_WORDS_FILE, 'r') as f:
                return json.load(f)
        return []

    def save_admins(self):
        with open(ADMIN_FILE, 'w') as f:
            json.dump(self.admins, f)

    def save_blocked_users(self):
        with open(BLOCKED_USERS_FILE, 'w') as f:
            json.dump(self.blocked_users, f)

    def save_filtered_words(self):
        with open(FILTERED_WORDS_FILE, 'w') as f:
            json.dump(self.filtered_words, f)

    def is_admin(self, username):
        return username in self.admins

    def is_blocked(self, username):
        return username in self.blocked_users

    def filter_message(self, message):
        for word in self.filtered_words:
            message = message.replace(word, '*' * len(word))
        return message

    def show_admin_panel(self):
        st.sidebar.markdown("### 관리자 패널")
        
        # 사용자 차단/해제
        st.sidebar.markdown("#### 사용자 차단/해제")
        block_username = st.sidebar.text_input("차단할 사용자명")
        if st.sidebar.button("차단"):
            if block_username and block_username not in self.blocked_users:
                self.blocked_users.append(block_username)
                self.save_blocked_users()
                st.sidebar.success(f"{block_username} 차단됨")
        if st.sidebar.button("차단 해제"):
            if block_username and block_username in self.blocked_users:
                self.blocked_users.remove(block_username)
                self.save_blocked_users()
                st.sidebar.success(f"{block_username} 차단 해제됨")
        
        # 부적절한 콘텐츠 필터링
        st.sidebar.markdown("#### 부적절한 콘텐츠 필터링")
        new_filtered_word = st.sidebar.text_input("필터링할 단어 추가")
        if st.sidebar.button("추가"):
            if new_filtered_word and new_filtered_word not in self.filtered_words:
                self.filtered_words.append(new_filtered_word)
                self.save_filtered_words()
                st.sidebar.success(f"{new_filtered_word} 필터링 단어 추가됨")
        if st.sidebar.button("제거"):
            if new_filtered_word and new_filtered_word in self.filtered_words:
                self.filtered_words.remove(new_filtered_word)
                self.save_filtered_words()
                st.sidebar.success(f"{new_filtered_word} 필터링 단어 제거됨")
