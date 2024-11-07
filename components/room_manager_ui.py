import streamlit as st
from services.room_manager import RoomManager

class RoomManagerUI:
    def __init__(self):
        self.room_manager = RoomManager()

    def show_room_list(self):
        """채팅방 목록을 표시합니다."""
        st.markdown("### 💭 채팅방 목록")
        rooms = self.room_manager.load_rooms()
        
        if not rooms:
            st.info("현재 활성화된 채팅방이 없습니다.")
            return

        for room_id, room_data in rooms.items():
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    room_info = f"""
                    ### 🏠 {room_data['name']}
                    """
                    if room_data['topic']:
                        room_info += f"\n📌 주제: {room_data['topic']}"
                    if not room_data['is_public']:
                        room_info += "\n🔒 비공개방"
                    room_info += f"\n👥 참여자 수: {len(room_data['members'])}명"
                    st.markdown(room_info)
                
                with col2:
                    if st.button("입장하기", key=f"join_{room_id}"):
                        st.session_state.current_room = room_id
                        st.session_state.show_room = True
                        st.rerun()
                st.markdown("---")

    def show_create_room_form(self):
        st.markdown("### 💬 새로운 채팅방 만들기")
        with st.form("create_room_form"):
            name = st.text_input("채팅방 이름")
            topic = st.text_input("주제 (선택사항)")
            is_public = st.checkbox("공개 채팅방", value=True)
            password = None
            if not is_public:
                password = st.text_input("비밀번호", type="password")
            
            if st.form_submit_button("채팅방 만들기"):
                if name:
                    room = self.room_manager.create_room(
                        name=name,
                        owner=st.session_state.username,
                        is_public=is_public,
                        password=password,
                        topic=topic
                    )
                    st.session_state.current_room = room.id
                    st.session_state.show_create_room = False
                    st.session_state.show_room = True
                    st.success(f"'{name}' 채팅방이 생성되었습니다!")
                    st.rerun()
                else:
                    st.error("채팅방 이름을 입력해주세요.")

    def show_room_settings(self, room_id):
        room = self.room_manager.get_room(room_id)
        if room and room.owner == st.session_state.username:
            st.markdown("### ⚙️ 채팅방 설정")
            
            topic = st.text_input("주제", value=room.topic or "")
            is_public = st.checkbox("공개 채팅방", value=room.is_public)
            notifications = st.checkbox("알림 켜기", value=room.notifications_enabled)
            
            new_password = None
            if not is_public:
                new_password = st.text_input("새 비밀번호", type="password")
            
            if st.button("설정 저장"):
                self.room_manager.update_room_settings(
                    room_id,
                    st.session_state.username,
                    topic=topic,
                    is_public=is_public,
                    password=new_password if new_password else room.password,
                    notifications_enabled=notifications
                )
                st.success("설정이 저장되었습니다!")

    def show_member_management(self, room_id):
        room = self.room_manager.get_room(room_id)
        if room:
            st.markdown("### 👥 멤버 관리")
            
            # 초대
            if st.session_state.username in room.members:
                new_member = st.text_input("초대할 사용자 닉네임")
                if st.button("초대하기"):
                    if self.room_manager.invite_user(room_id, new_member, st.session_state.username):
                        st.success(f"{new_member}님을 초대했습니다.")
                    else:
                        st.error("초대할 수 없습니다.")

            # 멤버 목록
            st.markdown("#### 현재 멤버")
            for member in room.members:
                col1, col2 = st.columns([3, 1])
                col1.write(member)
                if room.owner == st.session_state.username and member != room.owner:
                    if col2.button("강퇴", key=f"kick_{member}"):
                        if self.room_manager.kick_user(room_id, member, st.session_state.username):
                            st.success(f"{member}님을 강퇴했습니다.")
                            st.rerun()
