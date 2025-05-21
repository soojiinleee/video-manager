from datetime import datetime, timedelta
from typing import Union

from fastapi import HTTPException, status
from jose import JWTError, jwt

from src.core.config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_WEEKS,
    REFRESH_TOKEN_EXPIRE_WEEKS,
)

TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"

CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="유효한 토큰이 아닙니다.",
    headers={"WWW-Authenticate": "Bearer"},
)


def create_token(data: dict, expires_delta: timedelta) -> str:
    """공통 JWT 토큰 생성 함수"""
    to_encode = data.copy()
    expire = datetime.now() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(data: dict) -> str:
    """Access 토큰 생성"""
    return create_token(data, timedelta(weeks=ACCESS_TOKEN_EXPIRE_WEEKS))


def create_refresh_token(data: dict) -> str:
    """Refresh 토큰 생성"""
    return create_token(data, timedelta(weeks=REFRESH_TOKEN_EXPIRE_WEEKS))


def verify_access_token(token: str) -> int:
    """Access 토큰 유효성 검증 및 user_id 반환"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: Union[str, None] = payload.get("sub")

        if user_id is None:
            raise CREDENTIALS_EXCEPTION

        return int(user_id)
    except (JWTError, ValueError):
        raise CREDENTIALS_EXCEPTION
