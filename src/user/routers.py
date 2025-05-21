from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.auth.permissions import admin_required, get_current_user
from src.core.schemas import ErrorResponse
from src.user import service as user_svc
from src.user import exceptions as user_exceptions
from src.user.schemas import UserCreate, UserRead, AdminUserUpdate, PasswordUpdate
from src.user.models import User


router = APIRouter(prefix="/user", tags=["user"])
admin_router = APIRouter(prefix="/admin/user", tags=["admin"])


@admin_router.post(
    "/new",
    status_code=status.HTTP_201_CREATED,
    response_model=UserRead,
    summary="일반 유저 생성",
    responses={
        status.HTTP_409_CONFLICT: {
            "model": ErrorResponse,
            "description": user_exceptions.DuplicateDataException().detail,
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorResponse,
            "description": user_exceptions.UnauthorizedAccessException().detail,
        },
    },
)
async def create_user_by_admin(
    data: UserCreate,
    current_user: User = Depends(admin_required),
    db: AsyncSession = Depends(get_db),
):
    """
    일반 유저 생성
    - 토큰 필수
    - 어드민 계정만 생성 가능
    - 비밀번호 입력 안 하는 경우 이메일로 초기 비밀번호 설정
    """

    org_id = current_user.organization_id
    user = await user_svc.create_user_by_admin(db=db, org_id=org_id, data=data)

    return UserRead.from_orm(user)


@admin_router.put(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    summary="일반 유저 정보 변경",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": user_exceptions.UserNotFoundException().detail,
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorResponse,
            "description": user_exceptions.UnauthorizedAccessException().detail,
        },
    },
)
async def update_user_by_admin(
    data: AdminUserUpdate,
    user_id: int = Path(..., description="수정 유저 ID"),
    current_user: User = Depends(admin_required),
    db: AsyncSession = Depends(get_db),
):
    """
    일반 유저의 비밀번호 or 어드민 권한 수정 by 어드민 유저
    - 어드민 토큰 필수
    - 어드민 유저의 기업과 수정하려는 유저의 기업이 일치해야 함
    """
    return await user_svc.update_user_by_admin(
        db=db, data=data, admin=current_user, user_id=user_id
    )


@router.put(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    summary="유저 비밀번호 변경",
)
async def update_user(
    data: PasswordUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    로그인 유저의 비밀번호 변경
    - 토큰 필수
    """
    return await user_svc.update_user(
        db=db, new_password=data.new_password, user=current_user
    )


@admin_router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    summary="유저 삭제",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": user_exceptions.UserNotFoundException().detail,
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorResponse,
            "description": user_exceptions.UnauthorizedAccessException().detail,
        },
    },
)
async def delete_user_by_admin(
    user_id: int,
    current_user: User = Depends(admin_required),
    db: AsyncSession = Depends(get_db),
):
    """
    유저 삭제 by 어드민 유저
    - 어드민 토큰 필수
    - 어드민 유저의 기업과 삭제하려는 유저의 기업이 일치해야 함
    """
    return await user_svc.soft_delete_user_by_admin(
        db=db, admin=current_user, user_id=user_id
    )


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    summary="유저 탈퇴",
)
async def delete_user(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    로그인 유저 탈퇴
    - 토큰 필수
    """
    return await user_svc.soft_delete_user(db=db, user=current_user)
