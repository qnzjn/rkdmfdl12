import streamlit as st
import time

def show_notification(username):
    """채팅방 입장 알림을 표시합니다."""
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.info(f"🎉 {username}님이 채팅방에 입장하셨습니다!")
            time.sleep(2)

def show_exit_notification(username):
    """채팅방 퇴장 알림을 표시합니다."""
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.warning(f"👋 {username}님이 채팅방을 나가셨습니다.")
            time.sleep(2)
