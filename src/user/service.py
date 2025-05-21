from aioredlock.errors import AioredlockError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import LOCK_MANAGER
from src.auth.serivce import hash_password
from src.user import repository as user_repo
from src.user import exceptions as user_exceptions
from src.user.models import User
from src.user.schemas import UserCreate, AdminUserUpdate


async def create_user_by_admin(db: AsyncSession, org_id: int, data: UserCreate) -> User:
    """비밀번호 None인 경우 이메일을 초기 비밀번호로 설정"""

    if data.password is None:
        data.password = data.email

    return await user_repo.create_user(db=db, org_id=org_id, data=data)


async def update_user(db: AsyncSession, new_password: str, user: User):
    """유저 본인 비밀번호 변경"""
    hashed_pw = hash_password(new_password)
    await user_repo.update_user_password(db, user.id, hashed_pw)


async def update_user_by_admin(
    db: AsyncSession, data: AdminUserUpdate, admin: User, user_id: int
):
    """어드민이 다른 유저 정보 수정"""
    user = await user_repo.get_user(db, user_id)

    if not user:
        raise user_exceptions.UserNotFoundException

    if user.organization_id != admin.organization_id:
        raise user_exceptions.UnauthorizedAccessException

    if data.new_password:
        hashed_pw = hash_password(data.new_password)
        await user_repo.update_user_password(db, user_id, hashed_pw)

    if data.is_admin is not None:
        await user_repo.update_user_admin_status(db, user_id, data.is_admin)


async def soft_delete_user(db: AsyncSession, user: User):
    """본인 계정 삭제"""
    await user_repo.soft_delete_user_by_id(db, user_id=user.id)


async def soft_delete_user_by_admin(db: AsyncSession, admin: User, user_id: int):
    """어드민이 같은 조직의 유저를 soft delete"""

    user = await user_repo.get_user(db, user_id)

    if not user:
        raise user_exceptions.UserNotFoundException

    if user.organization_id != admin.organization_id:
        raise user_exceptions.UnauthorizedAccessException

    await user_repo.soft_delete_user_by_id(db, user_id=user_id)


async def add_user_video_point_with_lock(
    db: AsyncSession, user_id: int, video_id: int
) -> None:
    """
    유저 포인트 등록 - 분산락 구현 (with redis redlock)

    :param user_id int: 영상 조회한 유저, 포인트 적립 받을 유저 id
    :param video_id int: 조회한 영상 id
    :return None
    :raise redis lock 오류
    """

    lock_key = f"user_id:{user_id}:video:{video_id}:lock"
    lock = None

    try:
        lock = await LOCK_MANAGER.lock(lock_key, lock_timeout=10000)
        await user_repo.add_user_video_point(db, user_id, video_id)

    except AioredlockError as e:
        print("[ERROR]", e)
        raise user_exceptions.AddPointException

    finally:
        if lock:
            await LOCK_MANAGER.unlock(lock)
