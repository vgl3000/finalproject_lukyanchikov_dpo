
import hashlib

from valutatrade_hub.core.models import User
from valutatrade_hub.infra.storage import load_users, save_users


def register(username, password):
    users = load_users()

    for user in users:
        if user["username"] == username:
            raise ValueError("Такое имя уже занято")

    new_id = 1

    for user in users:
        if user["user_id"] >= new_id:
            new_id = user["user_id"] + 1

    new_user = User(new_id, username, password)

    users.append(new_user.to_dict())
    save_users(users)

    return f"Пользователь {username} зарегистрирован"


def login(username, password):
    users = load_users()

    for user in users:
        if user["username"] == username:
            password_hash = hashlib.sha256(
                (password + user["salt"]).encode("utf-8")
            ).hexdigest()

            if password_hash != user["hashed_password"]:
                raise ValueError("Неверный пароль")

            return f"Вы вошли как '{username}'"

    raise ValueError("Пользователь не найден")
