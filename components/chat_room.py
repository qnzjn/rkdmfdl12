import json
import os
from datetime import datetime

ROOMS_FILE = "data/chat_rooms.json"

class ChatRoom:
    def __init__(self, name, owner, is_public=True, password=None):
        self.id = str(hash(f"{name}_{datetime.now().timestamp()}"))
        self.name = name
        self.owner = owner
        self.is_public = is_public
        self.password = password
        self.members = [owner]
        self.invited_users = []
        self.messages = []
        self.created_at = datetime.now().isoformat()

class ChatRoomManager:
    def __init__(self):
        self.rooms = self.load_rooms()

    def load_rooms(self):
        if os.path.exists(ROOMS_FILE):
            with open(ROOMS_FILE, 'r') as f:
                data = json.load(f)
                return {room_id: ChatRoom(**room_data) for room_id, room_data in data.items()}
        return {}

    def save_rooms(self):
        data = {
            room_id: {
                'name': room.name,
                'owner': room.owner,
                'is_public': room.is_public,
                'password': room.password,
                'members': room.members,
                'invited_users': room.invited_users,
                'messages': room.messages,
                'created_at': room.created_at
            } for room_id, room in self.rooms.items()
        }
        with open(ROOMS_FILE, 'w') as f:
            json.dump(data, f)

    def create_room(self, name, owner, is_public=True, password=None):
        room = ChatRoom(name, owner, is_public, password)
        self.rooms[room.id] = room
        self.save_rooms()
        return room.id

    def delete_room(self, room_id, username):
        if room_id in self.rooms and self.rooms[room_id].owner == username:
            del self.rooms[room_id]
            self.save_rooms()
            return True
        return False

    def invite_user(self, room_id, username, invited_by):
        room = self.rooms.get(room_id)
        if room and invited_by in room.members:
            if username not in room.invited_users and username not in room.members:
                room.invited_users.append(username)
                self.save_rooms()
                return True
        return False

    def join_room(self, room_id, username, password=None):
        room = self.rooms.get(room_id)
        if room:
            if room.is_public or username in room.invited_users:
                if room.password and password != room.password:
                    return False, "잘못된 비밀번호입니다."
                if username not in room.members:
                    room.members.append(username)
                    if username in room.invited_users:
                        room.invited_users.remove(username)
                    self.save_rooms()
                return True, "채팅방에 입장했습니다."
            return False, "초대된 사용자만 입장할 수 있습니다."
        return False, "존재하지 않는 채팅방입니다."

    def leave_room(self, room_id, username):
        room = self.rooms.get(room_id)
        if room and username in room.members:
            room.members.remove(username)
            if username == room.owner and room.members:
                room.owner = room.members[0]
            elif username == room.owner and not room.members:
                del self.rooms[room_id]
            self.save_rooms()
            return True
        return False

    def kick_user(self, room_id, username, kicked_by):
        room = self.rooms.get(room_id)
        if room and kicked_by == room.owner and username in room.members:
            room.members.remove(username)
            self.save_rooms()
            return True
        return False

    def clear_all_rooms(self):
        """모든 채팅방 삭제"""
        self.rooms = {}
        if os.path.exists(ROOMS_FILE):
            os.remove(ROOMS_FILE)
        return True

    def get_room(self, room_id):
        return self.rooms.get(room_id)
