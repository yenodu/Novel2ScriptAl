import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, Header, HTTPException
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from database import get_db
from models import User

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "novel2scriptal-dev-secret-change-in-prod")
ALGORITHM = "HS256"
TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------------------------------------------------------------------
# Password helpers
# ---------------------------------------------------------------------------
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------
def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=TOKEN_EXPIRE_DAYS)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


# ---------------------------------------------------------------------------
# Auth dependency
# ---------------------------------------------------------------------------
def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization:
        raise HTTPException(status_code=401, detail="缺少认证 token，请先登录")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="认证格式错误，需要 Bearer token")

    token = authorization[7:]  # strip "Bearer "

    try:
        payload = decode_token(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="token 无效或已过期，请重新登录")

    user_id = int(payload.get("sub", 0))
    user = db.query(User).filter_by(id=user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在")

    return user
