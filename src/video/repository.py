from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, and_
from sqlalchemy.orm import joinedload

from src.video.models import Video
from src.video import exceptions as video_exceptions


async def get_video_by_id(db: AsyncSession, video_id: int) -> Video:
    stmt = (
        select(Video)
        .options(joinedload(Video.organization))
        .where(and_(Video.id == video_id, Video.is_deleted == False))
    )
    query = await db.execute(stmt)
    return query.scalar_one_or_none()


async def update_video_fields(
    db: AsyncSession, video: Video, title: str | None, description: str | None
):
    try:
        if title:
            video.title = title
        if description:
            video.description = description

        await db.commit()
    except SQLAlchemyError as e:
        await db.rollback()
        print("[ERROR]", e)
        raise video_exceptions.VideoUpdateFailedException


async def soft_delete_video(db: AsyncSession, video: Video):
    """영상 삭제 - soft delete"""

    try:
        video.is_deleted = True
        video.deleted_at = datetime.now()
        await db.commit()

    except SQLAlchemyError as e:
        await db.rollback()
        print("[ERROR]", e)
        raise video_exceptions.VideoDeleteFailedException


async def get_deleted_video_by_id(db: AsyncSession, video_id: int) -> Video | None:
    stmt = (
        select(Video)
        .options(joinedload(Video.organization))
        .where(Video.id == video_id, Video.is_deleted.is_(True))
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def restore_video(db: AsyncSession, video: Video):
    try:
        video.is_deleted = False
        video.deleted_at = None

        await db.commit()
    except SQLAlchemyError as e:
        await db.rollback()
        print("[ERROR]", e)
        raise video_exceptions.VideoRestoreFailedException
