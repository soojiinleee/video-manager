from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import select, update, and_
from sqlalchemy.orm import joinedload

from src.user.models import User, UserVideoPoint
from src.user.schemas import UserCreate
from src.user.exceptions import DuplicateDataException


async def get_user(db: AsyncSession, user_id: int) -> Optional[User]:
    stmt = (
        select(User)
        .options(joinedload(User.organization))
        .where(and_(User.id == user_id, User.is_active == True))
    )
    query = await db.execute(stmt)
    user = query.scalar()
    return user


async def get_active_user_by_email_and_org(
    db: AsyncSession, email: str, organization_id: int
) -> Optional[User]:
    stmt = select(User).where(
        and_(
            User.email == email,
            User.organization_id == organization_id,
            User.is_active == True,
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_admin_user(
    db: AsyncSession, org_id: int, email: str, password: str
) -> User:
    user = User(
        organization_id=org_id,
        email=email,
        is_admin=True,
    )
    user.set_password(password)
    db.add(user)
    await db.flush()

    return user


async def create_user(db: AsyncSession, org_id: int, data: UserCreate) -> User:
    try:
        user = User(
            organization_id=org_id,
            email=data.email,
        )
        user.set_password(data.password)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    except IntegrityError:
        raise DuplicateDataException


async def update_user_password(db: AsyncSession, user_id: int, hashed_password: str):
    stmt = (
        update(User).where(User.id == user_id).values(hashed_password=hashed_password)
    )
    await db.execute(stmt)
    await db.commit()


async def update_user_admin_status(db: AsyncSession, user_id: int, is_admin: bool):
    stmt = update(User).where(User.id == user_id).values(is_admin=is_admin)
    await db.execute(stmt)
    await db.commit()


async def soft_delete_user_by_id(db: AsyncSession, user_id: int):
    stmt = (
        update(User)
        .where(User.id == user_id)
        .values(is_active=False, deactivated_at=datetime.now())
    )
    await db.execute(stmt)
    await db.commit()


async def add_user_video_point(db: AsyncSession, user_id: int, video_id: int):
    try:
        add_point = UserVideoPoint(
            user_id=user_id,
            video_id=video_id,
        )
        db.add(add_point)
        await db.commit()

        return
    except SQLAlchemyError as e:
        await db.rollback()
        print("[ERROR]", e)
