import json
import os
from datetime import datetime


USERS_FILE = 'users.json'


def load_users():
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users,f,indent=2,ensure_ascii=False)

def register_user(user_id,username, first_name):
    users = load_users()

    if str(user_id) not in users:
        users[str(user_id)] = {
            "username": username,
            "first_name": first_name,
            "message_count": 0,
            "registered": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_activity": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_users(users)
        return True
    return False

def increment_message_count(user_id):
    users = load_users()
    user_id_str = str(user_id)

    if user_id_str in users:
        users[user_id_str]["message_count"] += 1
        users[user_id_str]["last_activity"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        save_users(users)

