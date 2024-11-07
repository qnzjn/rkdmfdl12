import os
import json
from models.room import ChatRoom

class RoomManager:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.rooms_file = os.path.join(data_dir, "rooms.json")
        self.ensure_data_file()

    def ensure_data_file(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        if not os.path.exists(self.rooms_file):
            with open(self.rooms_file, 'w') as f:
                json.dump({}, f)

    def create_room(self, name, owner, is_public=True, password=None, topic=None):
        room = ChatRoom(name, owner, is_public, password, topic)
        self.save_room(room)
        return room

    def save_room(self, room):
        rooms = self.load_rooms()
        rooms[room.id] = room.to_dict()
        with open(self.rooms_file, 'w') as f:
            json.dump(rooms, f)

    def load_rooms(self):
        with open(self.rooms_file, 'r') as f:
            return json.load(f)

    def get_room(self, room_id):
        rooms = self.load_rooms()
        if room_id in rooms:
            return ChatRoom.from_dict(rooms[room_id])
        return None

    def delete_room(self, room_id, user):
        rooms = self.load_rooms()
        if room_id in rooms:
            room = ChatRoom.from_dict(rooms[room_id])
            if room.owner == user:
                del rooms[room_id]
                with open(self.rooms_file, 'w') as f:
                    json.dump(rooms, f)
                return True
        return False

    def invite_user(self, room_id, user_to_invite, inviting_user):
        room = self.get_room(room_id)
        if room and inviting_user in room.members:
            if user_to_invite not in room.banned_users:
                if user_to_invite not in room.members:
                    room.members.append(user_to_invite)
                    self.save_room(room)
                    return True
        return False

    def kick_user(self, room_id, user_to_kick, admin_user):
        room = self.get_room(room_id)
        if room and admin_user == room.owner:
            if user_to_kick in room.members and user_to_kick != room.owner:
                room.members.remove(user_to_kick)
                room.banned_users.append(user_to_kick)
                self.save_room(room)
                return True
        return False

    def update_room_settings(self, room_id, user, **settings):
        room = self.get_room(room_id)
        if room and room.owner == user:
            for key, value in settings.items():
                if hasattr(room, key):
                    setattr(room, key, value)
            self.save_room(room)
            return True
        return False
