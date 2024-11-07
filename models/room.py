from datetime import datetime
import json
import os

class ChatRoom:
    def __init__(self, name, owner, is_public=True, password=None, topic=None):
        self.id = str(hash(f"{name}{datetime.now().isoformat()}"))
        self.name = name
        self.owner = owner
        self.is_public = is_public
        self.password = password
        self.topic = topic
        self.members = [owner]
        self.banned_users = []
        self.created_at = datetime.now().isoformat()
        self.notifications_enabled = True

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "owner": self.owner,
            "is_public": self.is_public,
            "password": self.password,
            "topic": self.topic,
            "members": self.members,
            "banned_users": self.banned_users,
            "created_at": self.created_at,
            "notifications_enabled": self.notifications_enabled
        }

    @staticmethod
    def from_dict(data):
        room = ChatRoom(data["name"], data["owner"])
        room.id = data["id"]
        room.is_public = data["is_public"]
        room.password = data["password"]
        room.topic = data["topic"]
        room.members = data["members"]
        room.banned_users = data["banned_users"]
        room.created_at = data["created_at"]
        room.notifications_enabled = data.get("notifications_enabled", True)
        return room
