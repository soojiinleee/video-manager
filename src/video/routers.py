from fastapi import APIRouter, Depends, Form, UploadFile, File, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.core.schemas import ErrorResponse
from src.core.celery.tasks import video as task_video
from src.auth.permissions import admin_required, get_current_user, paid_admin_required
from src.user.models import User
from src.user.exceptions import AddPointException
from src.video import exceptions as video_exceptions
from src.video import service as video_svc
from src.video.scehmas import VideoRead
from src.video.utils import save_temp_file

router = APIRouter(prefix="/video", tags=["video"])
admin_router = APIRouter(prefix="/admin/video", tags=["admin"])


@admin_router.post("/new", status_code=status.HTTP_202_ACCEPTED, summary="영상 업로드")
async def upload_video_by_admin(
    title=Form(min_length=2, max_length=250, description="영상 제목"),
    description=Form(None, min_length=2, description="영상 설명"),
    video_file: UploadFile | None = File(None, description="영상 파일"),
    admin: User = Depends(admin_required),
):
    """
    영상 업로드 by 어드민
     - request content type: form-data
    - 어드민 토큰 필수
    """
    tmp_path = await save_temp_file(video_file)

    data = {
        "title": title,
        "description": description or title,
        "tmp_path": tmp_path,
        "user_id": admin.id,
        "organization_id": admin.organization_id,
    }
    task_video.process_video_upload.delay(data)

    return {"message": "업로드 요청이 접수 되었습니다."}


@admin_router.put(
    "/{video_id}",
    status_code=status.HTTP_202_ACCEPTED,
    summary="영상 수정",
)
async def update_video_by_admin(
    video_id: int = Path(..., description="영상 ID"),
    title=Form(None, min_length=2, max_length=250, description="영상 제목"),
    description=Form(None, min_length=2, description="영상 설명"),
    video_file: UploadFile | None = File(None, description="영상 파일"),
    admin: User = Depends(admin_required),
    db: AsyncSession = Depends(get_db),
):
    """
    영상 수정 by 어드민
    - request content type: form-data
    - 어드민 토큰 필수
    - 최초 영상 업로드 기업 ID와 수정 시도하는 어드민 기업 일치해야 함
    - 파일 없이 제목과 설명만 수정 가능
    """
    # 1. 수정 가능한 비디오 확인
    video = await video_svc.can_modify_video(db=db, video_id=video_id, admin=admin)

    # 2. 파일이 포함된 경우 -> 비동기 처리
    if video_file and video_file.filename.strip():
        tmp_path = await save_temp_file(video_file)

        task_data = {
            "video_id": video_id,
            "title": title,
            "description": description,
            "tmp_path": tmp_path,
            "organization_id": admin.organization_id,
        }
        task_video.process_video_update.delay(task_data)
        return {"message": "영상 업데이트가 접수 되었습니다."}

    # 3. 파일 없는 경우 업데이트
    await video_svc.update_video_meta(
        db=db, video=video, title=title, description=description
    )

    return VideoRead.model_validate(video)


@admin_router.delete(
    "/{video_id}", status_code=status.HTTP_204_NO_CONTENT, summary="영상 삭제"
)
async def delete_video_by_admin(
    video_id: int = Path(..., description="영상 ID"),
    admin: User = Depends(admin_required),
    db: AsyncSession = Depends(get_db),
):
    """
    영상 삭제 by 어드민
    - 어드민 토큰 필수
    """
    return await video_svc.soft_delete_video_by_admin(
        db=db, video_id=video_id, admin=admin
    )


@admin_router.put(
    "/{video_id}/restore",
    response_model=VideoRead,
    summary="영상 복구",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": video_exceptions.VideoNotFoundException().detail,
        },
    },
)
async def restore_video(
    video_id: int = Path(..., description="영상 ID"),
    admin: User = Depends(paid_admin_required),
    db: AsyncSession = Depends(get_db),
):
    """
    삭제한 영상 복구 by 어드민
    - 어드민 토큰 필수
    - 어드민의 기업이 유료 플랜 구독 중인 경우 복구 가능
    - 복구 영상의 업로드 기업과 어드민 기업 일치해야 함
    """
    video = await video_svc.restore_video_by_admin(
        db=db, video_id=video_id, admin=admin
    )

    return VideoRead.model_validate(video)


@router.get(
    "/{video_id}",
    summary="영상 조회",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": video_exceptions.VideoNotFoundException().detail,
        },
        status.HTTP_429_TOO_MANY_REQUESTS: {
            "model": ErrorResponse,
            "description": AddPointException().detail,
        },
    },
)
async def read_video(
    video_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    영상 조회
    - 토큰 필수
    - 영상 조회 시 포인트 적립
    """

    return await video_svc.get_video_stream_with_point(
        db=db, video_id=video_id, user=current_user
    )
