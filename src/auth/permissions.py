from typing import Annotated, Callable
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.auth.token import verify_access_token
from src.organization.repository import is_paid_plan
from src.user.models import User
from src.user.repository import get_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: AsyncSession = Depends(get_db)
) -> User:
    user_id = verify_access_token(token)
    user = await get_user(db, user_id)

    # 소속 기업의 유료 플랜 이용 여부 확인
    user.is_paid = await is_paid_plan(db, user.organization_id)
    return user


class RequireRole:
    """역할별 권한 확인 클래스"""

    def __init__(self, check: Callable[[User], bool], error_message: str):
        self.check = check
        self.error_message = error_message

    async def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if not self.check(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=self.error_message,
            )
        return current_user


admin_required = RequireRole(
    check=lambda user: user.is_admin, error_message="관리자 권한이 필요합니다."
)

paid_admin_required = RequireRole(
    check=lambda user: user.is_admin and user.is_paid,
    error_message="결제가 필요한 서비스 입니다.",
)
