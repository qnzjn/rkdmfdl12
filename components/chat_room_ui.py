import streamlit as st
from .chat_room import ChatRoomManager

class ChatRoomUI:
    def __init__(self):
        self.room_manager = ChatRoomManager()

    def show_create_room_form(self):
        st.markdown("### 새 채팅방 만들기")
        
        name = st.text_input("채팅방 이름")
        is_public = st.checkbox("공개 채팅방", value=True)
        password = None
        
        if not is_public:
            password = st.text_input("비밀번호 설정", type="password")
            
        if st.button("채팅방 만들기"):
            if name:
                room_id = self.room_manager.create_room(
                    name=name,
                    owner=st.session_state.username,
                    is_public=is_public,
                    password=password
                )
                st.success("채팅방이 생성되었습니다!")
                st.session_state.current_room = room_id
                st.session_state.show_room = True
                st.session_state.show_create_room = False
                st.rerun()
            else:
                st.error("채팅방 이름을 입력해주세요.")

    def show_room_list(self):
        st.markdown("### 채팅방 목록")
        
        rooms = self.room_manager.rooms
        if not rooms:
            st.info("현재 생성된 채팅방이 없습니다.")
            return

        for room_id, room in rooms.items():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                room_info = f"🏠 {room.name} ({len(room.members)}명)"
                if not room.is_public:
                    room_info += " 🔒"
                st.markdown(room_info)
                
            with col2:
                if st.button("입장하기", key=f"join_room_{room_id}"):
                    if room.is_public:
                        success, message = self.room_manager.join_room(room_id, st.session_state.username)
                    else:
                        password = st.text_input("비밀번호를 입력하세요", 
                                               type="password", 
                                               key=f"pwd_input_{room_id}")
                        if password:
                            success, message = self.room_manager.join_room(
                                room_id, 
                                st.session_state.username, 
                                password
                            )
                        else:
                            success, message = False, "비밀번호를 입력해주세요."
                    
                    if success:
                        st.session_state.current_room = room_id
                        st.session_state.show_room = True
                        st.rerun()
                    else:
                        st.error(message)
