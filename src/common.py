import bcrypt

from src.db import SessionLocal

def get_hashed_password(plain_text_password: str) -> str:
    return bcrypt.hashpw(plain_text_password, bcrypt.gensalt())

def check_password(plain_text_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_text_password, hashed_password)

def get_random_hash() -> str:
    return bcrypt.gensalt()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()