from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.core.schemas import ErrorResponse
from src.auth.schemas import Token
from src.auth.token import create_access_token, create_refresh_token
from src.auth.serivce import authenticate_user
from src.user.schemas import UserCredential
from src.auth.exceptions import InvalidCredentials

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=Token,
    summary="로그인",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorResponse,
            "description": InvalidCredentials().detail,
        },
    },
)
async def login(data: UserCredential, db: AsyncSession = Depends(get_db)):
    """
    기업 유저 별 로그인
    - 이메일 계정 같아도 기업이 다르면 로그인 가능
    - organization id 필수
    """
    user = await authenticate_user(db=db, data=data)

    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return Token(access_token=access_token, refresh_token=refresh_token)
