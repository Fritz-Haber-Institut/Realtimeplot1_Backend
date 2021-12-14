import hashlib

from flask import current_app


def get_hash(password: str):
    encoded_password=hashlib.md5(f"{current_app.config['PASSWORD_SALT']}{password}".encode())
    return encoded_password.hexdigest()

def check_password_hash(password: str, hash: str) -> bool:
    if get_hash(password) == hash:
        return True
    else:
        return False
