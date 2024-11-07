import streamlit as st
from datetime import datetime, timedelta
import os
import sys
import json
import pickle
from PIL import Image
import shutil
import time

# 채팅봇 관련 임포트 수정
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# chatbot 임포트를 위한 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# 나머지 임포트
try:
    from notifications.notification_manager import show_notification, show_exit_notification
    from components.room_manager_ui import RoomManagerUI
    from admin.admin_manager import AdminManager
    from components.chat_room_ui import ChatRoomUI
    from chatbot.bot_manager import BotManager
    CHATBOT_ENABLED = True
except ImportError as e:
    print(f"Import error: {str(e)}")
    CHATBOT_ENABLED = False

# 데이터 폴더 경로 설정
DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.txt")
SESSIONS_FILE = os.path.join(DATA_DIR, "sessions.pkl")
ACTIVE_USERS_FILE = os.path.join(DATA_DIR, "active_users.json")
SESSION_TIMEOUT = 300  # 5분 타임아웃

# 추가 상수 정의
PROFILE_DIR = os.path.join(DATA_DIR, "profiles")
PROFILES_FILE = os.path.join(DATA_DIR, "user_profiles.json")

# 관리자 초기화
admin_manager = AdminManager()

# bot_manager 초기화 함수 수정
def init_bot_manager():
    if not CHATBOT_ENABLED:
        return None
    try:
        return BotManager()
    except Exception as e:
        print(f"Bot manager initialization error: {str(e)}")
        return None

# 전역 봇 매니저 초기화
bot_manager = init_bot_manager()

def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(USERS_FILE):
        open(USERS_FILE, 'w').close()
    if not os.path.exists(SESSIONS_FILE):
        with open(SESSIONS_FILE, 'w') as f:
            json.dump({}, f)
    if not os.path.exists(ACTIVE_USERS_FILE):
        with open(ACTIVE_USERS_FILE, 'w') as f:
            json.dump({}, f)
    if not os.path.exists(PROFILE_DIR):
        os.makedirs(PROFILE_DIR)
    if not os.path.exists(PROFILES_FILE):
        with open(PROFILES_FILE, 'w') as f:
            json.dump({}, f)

def init_session_state():
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'username' not in st.session_state:
        st.session_state.username = ''
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'show_create_room' not in st.session_state:
        st.session_state.show_create_room = False
    if 'show_room' not in st.session_state:
        st.session_state.show_room = False
    if 'current_room' not in st.session_state:
        st.session_state.current_room = None
    if 'bot_welcomed' not in st.session_state:
        st.session_state.bot_welcomed = False
    if 'bot_enabled' not in st.session_state:
        st.session_state.bot_enabled = bot_manager is not None
        
    saved_session = load_session()
    if saved_session:
        st.session_state.username = saved_session
        st.session_state.authenticated = True

def load_users():
    if not os.path.exists(USERS_FILE):
        return set()
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        return set(f.read().splitlines())

def save_user(username):
    with open(USERS_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{username}\n")

def save_session(username):
    try:
        session_data = {
            'session_id': st.session_state.session_id,
            'username': username,
            'timestamp': datetime.now().isoformat()
        }
        with open(SESSIONS_FILE, 'wb') as f:
            pickle.dump(session_data, f)
        return True
    except Exception as e:
        st.error(f"세션 저장 실패: {str(e)}")
        return False

def load_session():
    try:
        if os.path.exists(SESSIONS_FILE):
            with open(SESSIONS_FILE, 'rb') as f:
                session_data = pickle.load(f)
                if session_data and 'username' in session_data:
                    return session_data['username']
    except Exception:
        pass
    return None

def remove_session():
    try:
        if os.path.exists(SESSIONS_FILE):
            os.remove(SESSIONS_FILE)
        return True
    except Exception:
        return False

def check_username(username, allow_current=False):
    """
    닉네임 유효성 검사 및 중복 체크
    allow_current: 현재 사용자의 닉네임은 허용 (닉네임 변경 시)
    """
    users = load_users()
    
    if not username or len(username.strip()) == 0:
        st.error('닉네임을 입력해주세요.')
        return False
        
    # 현재 사용자의 닉네임인 경우 허용
    if allow_current and username == st.session_state.username:
        return True
    
    # 기존 사용자인 경우 자동 허용
    if username in users:
        return True
        
    # 새로운 사용자 등록
    save_user(username)
    return True

def update_active_users():
    try:
        with open(ACTIVE_USERS_FILE, 'r+') as f:
            try:
                active_users = json.load(f)
            except json.JSONDecodeError:
                active_users = {}
            
            current_time = datetime.now()
            
            # 현재 사용자 업데이트
            if st.session_state.username:
                # 같은 사용자명의 이전 세션 제거
                active_users = {
                    sid: data for sid, data in active_users.items()
                    if data['username'] != st.session_state.username
                }
                
                # 현재 세션 추가
                active_users[st.session_state.session_id] = {
                    'username': st.session_state.username,
                    'last_active': current_time.isoformat()
                }
            
            # 비활성 세션 제거
            active_users = {
                sid: data for sid, data in active_users.items()
                if datetime.fromisoformat(data['last_active']) > current_time - timedelta(seconds=SESSION_TIMEOUT)
            }
            
            # 파일 업데이트
            f.seek(0)
            json.dump(active_users, f)
            f.truncate()
            
            # 중복 제거된 사용자 수 반환
            unique_users = len(set(data['username'] for data in active_users.values()))
            return unique_users
            
    except Exception as e:
        st.error(f"활성 사용자 업데이트 실패: {str(e)}")
        return 0

def remove_active_user():
    try:
        with open(ACTIVE_USERS_FILE, 'r+') as f:
            active_users = json.load(f)
            active_users.pop(st.session_state.session_id, None)
            f.seek(0)
            json.dump(active_users, f)
            f.truncate()
    except Exception:
        pass

def logout():
    username = st.session_state.username
    remove_session()
    remove_active_user()
    show_exit_notification(username)  # 퇴장 알림 추가
    st.session_state.username = ''
    st.session_state.messages = []
    st.rerun()

def load_css():
    try:
        with open(os.path.join('styles', 'main.css'), 'r', encoding='utf-8') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"CSS 로딩 실패: {str(e)}")

def load_profile(username):
    try:
        with open(PROFILES_FILE, 'r') as f:
            profiles = json.load(f)
            return profiles.get(username, {
                'image': 'default.png',
                'status': 'offline',
                'last_seen': None
            })
    except Exception:
        return {'image': 'default.png', 'status': 'offline', 'last_seen': None}

def save_profile(username, profile_data):
    try:
        with open(PROFILES_FILE, 'r+') as f:
            profiles = json.load(f)
            profiles[username] = profile_data
            f.seek(0)
            json.dump(profiles, f)
            f.truncate()
    except Exception as e:
        st.error(f"프로필 저장 실패: {str(e)}")

def profile_settings():
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("< 채팅방으로 돌아가기"):
            st.session_state.show_profile = False
            st.rerun()
    
    st.markdown("### ⚙️ 프로필 설정")
    
    profile = load_profile(st.session_state.username)
    
    # 현재 프로필 이미지 표시
    current_img_path = os.path.join(PROFILE_DIR, profile.get('image', 'default.png'))
    if (os.path.exists(current_img_path)):
        st.image(current_img_path, width=200, caption="현재 프로필 이미지")
    
    # 프로필 이미지 업로드
    uploaded_file = st.file_uploader("새 프로필 이미지 선택", type=['jpg', 'png', 'jpeg'])
    if uploaded_file:
        try:
            img = Image.open(uploaded_file)
            img = img.resize((200, 200))
            img_path = os.path.join(PROFILE_DIR, f"{st.session_state.username}.png")
            img.save(img_path)
            profile['image'] = f"{st.session_state.username}.png"
            save_profile(st.session_state.username, profile)
            st.success("프로필 이미지가 업데이트되었습니다!")
            st.rerun()
        except Exception as e:
            st.error(f"이미지 업로드 실패: {str(e)}")

    st.markdown("---")

    # 닉네임 변경
    st.subheader("닉네임 설정")
    new_username = st.text_input("새로운 닉네임", value=st.session_state.username)
    if st.button("닉네임 변경하기", key="change_username_btn"):
        if new_username and new_username != st.session_state.username:
            # 중복 체크 (현재 사용자의 닉네임은 허용)
            if check_username(new_username, allow_current=True):
                old_username = st.session_state.username
                
                # users.txt에서 이전 닉네임 제거
                users = load_users()
                users.discard(old_username)
                with open(USERS_FILE, 'w', encoding='utf-8') as f:
                    for user in users:
                        f.write(f"{user}\n")
                
                # 프로필 업데이트
                profile = load_profile(old_username)
                
                # 세션 업데이트
                st.session_state.username = new_username
                st.session_state.authenticated = True
                save_session(new_username)
                
                # ��로필 이미지 파일명 변경
                old_img = os.path.join(PROFILE_DIR, f"{old_username}.png")
                if os.path.exists(old_img):
                    new_img = os.path.join(PROFILE_DIR, f"{new_username}.png")
                    shutil.move(old_img, new_img)
                
                # 프로필 데이터 업데이트
                save_profile(new_username, profile)
                
                st.success("닉네임이 변경되었습니다!")
                time.sleep(1)
                st.rerun()
        else:
            st.error("새로운 닉네임을 입력하세요.")

def update_user_status():
    profile = load_profile(st.session_state.username)
    profile['status'] = 'online'
    profile['last_seen'] = datetime.now().isoformat()
    save_profile(st.session_state.username, profile)

def format_last_seen(last_seen_str):
    if not last_seen_str:
        return "알 수 없음"
    last_seen = datetime.fromisoformat(last_seen_str)
    now = datetime.now()
    diff = now - last_seen
    
    if diff.total_seconds() < 60:
        return "방금 전"
    elif diff.total_seconds() < 3600:
        return f"{int(diff.total_seconds() / 60)}분 전"
    elif diff.total_seconds() < 86400:
        return f"{int(diff.total_seconds() / 3600)}시간 전"
    else:
        return last_seen.strftime("%Y-%m-%d %H:%M")

def sidebar_content():
    with st.sidebar:
        st.markdown("""
        <div class='sidebar-content'>
            <h2>채팅방 정보</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # 실시간 참여자 수 표시
        active_count = update_active_users()
        st.info(f"👥 실시간 참여자 수: {active_count}명")
        
        if st.session_state.username:
            profile = load_profile(st.session_state.username)
            
            # 프로필 이미지 표시
            img_path = os.path.join(PROFILE_DIR, profile.get('image', 'default.png'))
            if os.path.exists(img_path):
                st.image(img_path, width=100)
            
            st.success(f"✨ 환영합니다! {st.session_state.username}님")
            
            # 상태 표시
            status = profile.get('status', 'offline')
            st.markdown(f"""
                <div>
                    <span class='status-indicator status-{status}'></span>
                    {status.upper()}
                </div>
            """, unsafe_allow_html=True)
            
            # 마지막 접속 시간
            if profile.get('last_seen'):
                st.markdown(f"마지막 접속: {format_last_seen(profile['last_seen'])}")
            
            # 접속자 목록 부분 수정 - 한글 깨짐 해결
            st.markdown("### 👥 접속자 목록")
            try:
                with open(ACTIVE_USERS_FILE, 'r', encoding='utf-8') as f:
                    active_users = json.load(f)
                    unique_users = list(set(data['username'] for data in active_users.values()))
                    for username in unique_users:
                        st.markdown(f"• {username}")
            except Exception as e:
                st.error(f"접속자 목록 로딩 실패: {str(e)}")
            
            # 프로필 설정
            if st.button("프로필 설정"):
                st.session_state.show_profile = True
            
            if st.button('🚪 로그아웃', key='logout'):
                profile['status'] = 'offline'
                save_profile(st.session_state.username, profile)
                logout()

# 봇 응답 처리 함수 수정
def handle_bot_response(message, username):
    if not bot_manager:
        return None
    try:
        return bot_manager.process_message(message, username)
    except Exception as e:
        st.error(f"봇 응답 처리 실패: {str(e)}")
        return None

def main():
    load_css()
    
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(hash(datetime.now().strftime("%Y%m%d%H%M%S")))
    if 'show_profile' not in st.session_state:
        st.session_state.show_profile = False
    if 'just_entered' not in st.session_state:
        st.session_state.just_entered = False

    init_session_state()
    update_active_users()
    
    st.markdown("""
        <div class='main-title'>
            <h1>💬 실시간 채팅방</h1>
        </div>
    """, unsafe_allow_html=True)
    
    notification_container = st.container()
    with notification_container:
        if st.session_state.just_entered:
            show_notification(st.session_state.username)
            st.session_state.just_entered = False
    
    sidebar_content()

    # 프로필 설정 화면 표시
    if st.session_state.show_profile:
        profile_settings()
        return  # 프로필 설정 화면일 때는 나머지 UI 표시하지 않음

    # 로그인 전/후 화면 분리
    if not st.session_state.username:
        st.markdown("### 👋 환영합니다!")
        col1, col2 = st.columns([3, 1])
        with col1:
            username = st.text_input('닉네임을 입력하세요', 
                                   placeholder='닉네임을 입력해주세요',
                                   key='login_input')
        with col2:
            if st.button('입장하기', key='enter'):
                if username:
                    # 중복 체크 (초기 로그인)
                    if check_username(username, allow_current=False):
                        st.session_state.username = username
                        st.session_state.authenticated = True
                        st.session_state.just_entered = True
                        profile = load_profile(username)
                        profile['status'] = 'online'  # 상태 업데이트
                        save_profile(username, profile)
                        if save_session(username):
                            st.rerun()
                else:
                    st.error('닉네임을 입력해주세요.')

    # 채팅 컨테이너
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    
    # 채팅 메시지 표시
    if 'messages' in st.session_state:
        for message in st.session_state.messages:
            if not admin_manager.is_blocked(message["username"]):
                with st.chat_message(message['role']):
                    st.markdown(f"""
                        <div class='user-info'>
                            {message['username']} • {message['time']}
                        </div>
                        {admin_manager.filter_message(message['content'])}
                    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # 봇 웰컴 메시지 처리 부분 수정
    if (st.session_state.username and 
        not st.session_state.get('bot_welcomed', False) and 
        bot_manager is not None):
        try:
            welcome_message = bot_manager.get_welcome_message(st.session_state.username)
            if welcome_message:
                if 'messages' not in st.session_state:
                    st.session_state.messages = []
                st.session_state.messages.append(welcome_message)
                st.session_state.bot_welcomed = True
                st.rerun()
        except Exception as e:
            print(f"웰컴 메시지 처리 실패: {e}")

    # 메시지 입력 처리
    if st.session_state.username:
        message = st.chat_input("메시지를 입력하세요", key='message')
        if message:
            user_message = {
                "role": "user",
                "content": message,
                "username": st.session_state.username,
                "time": datetime.now().strftime("%H:%M")
            }
            if 'messages' not in st.session_state:
                st.session_state.messages = []
            
            # 봇 응답 처리 (욕설/비난 감지)
            if bot_manager:
                bot_response = handle_bot_response(message, st.session_state.username)
                if bot_response:
                    st.session_state.messages.append(bot_response)
                else:
                    # 문제없는 메시지만 추가
                    st.session_state.messages.append(user_message)
            else:
                st.session_state.messages.append(user_message)
            
            st.rerun()

if __name__ == "__main__":
    ensure_data_dir()
    if not os.path.exists('styles'):
        os.makedirs('styles')
    main()
