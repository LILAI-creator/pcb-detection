from datetime import datetime, timedelta
from typing import Optional

import jwt
from passlib.context import CryptContext

from app.config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_MINUTES
from app.database import SessionLocal
from app.models.db_models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(username: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {"sub": username, "exp": expire}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload.get("sub")
    except jwt.PyJWTError:
        return None


def register_user(username: str, password: str) -> dict:
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            return {"success": False, "message": "用户名已存在"}

        user = User(
            username=username,
            password_hash=hash_password(password),
        )
        db.add(user)
        db.commit()

        token = create_access_token(username)
        return {"success": True, "token": token, "username": username}
    except Exception:
        db.rollback()
        return {"success": False, "message": "注册失败"}
    finally:
        db.close()


def login_user(username: str, password: str) -> dict:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user or not verify_password(password, user.password_hash):
            return {"success": False, "message": "用户名或密码错误"}

        token = create_access_token(username)
        return {"success": True, "token": token, "username": username}
    finally:
        db.close()


def get_user_id_by_username(username: str) -> Optional[int]:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        return user.id if user else None
    finally:
        db.close()
