from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.user.models import User
from src.user.service import add_user_video_point_with_lock
from src.video import repository as video_repo
from src.video import exceptions as video_exceptions
from src.video.utils import stream_video
from src.video.models import Video


async def can_modify_video(db: AsyncSession, video_id: int, admin: User) -> Video:
    """영상 수정 가능 여부 확인"""

    video = await video_repo.get_video_by_id(db, video_id)
    if video is None:
        raise video_exceptions.VideoNotFoundException

    if video.organization_id != admin.organization_id:
        raise video_exceptions.UnauthorizedAccessException

    return video


async def update_video_meta(
    db: AsyncSession, video: Video, title: str | None, description: str | None
):
    """파일 없이 영상 정보만 수정"""

    await video_repo.update_video_fields(db, video, title, description)


async def soft_delete_video_by_admin(db: AsyncSession, video_id: int, admin: User):
    """어드민 영상 삭제"""

    video = await can_modify_video(db=db, video_id=video_id, admin=admin)

    if video:
        await video_repo.soft_delete_video(db=db, video=video)


async def get_restorable_video(db: AsyncSession, video_id: int, admin: User) -> Video:
    video = await video_repo.get_deleted_video_by_id(db, video_id)

    if video is None:
        raise video_exceptions.VideoNotFoundException

    if video.organization_id != admin.organization_id:
        raise video_exceptions.UnauthorizedAccessException

    return video


async def restore_video_by_admin(db: AsyncSession, video_id: int, admin: User):
    video = await get_restorable_video(db=db, video_id=video_id, admin=admin)

    if video:
        await video_repo.restore_video(db=db, video=video)

    return video


async def get_video_stream_with_point(
    db: AsyncSession,
    video_id: int,
    user: User,
) -> StreamingResponse:
    """일반 유저 비디오 조회 + 포인트 적립 + 스트리밍 응답 생성"""

    video: Video = await video_repo.get_video_by_id(db, video_id)

    if not video or not video.path:
        raise video_exceptions.VideoNotFoundException

    # 포인트 적립
    await add_user_video_point_with_lock(db=db, user_id=user.id, video_id=video.id)

    # 스트리밍 생성
    video_stream = stream_video(video.path)

    return StreamingResponse(video_stream, media_type="video/mp4")
