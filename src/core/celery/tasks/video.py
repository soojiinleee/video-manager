from sqlalchemy import select, and_
from sqlalchemy.exc import SQLAlchemyError

from src.db.sync_session import sync_session
from src.core.celery.app import celery_app
from src.video.models import Video
from src.video.utils import upload_video_file


@celery_app.task(name="process_video_upload")
def process_video_upload(payload: dict):
    """영상 업로드 및 저장"""

    user_id = payload["user_id"]
    organization_id = payload["organization_id"]
    title = payload["title"]
    description = payload["description"]
    tmp_path = payload["tmp_path"]

    try:
        dest_path = upload_video_file(tmp_path, organization_id)
    except Exception as file_error:
        print("[ERROR] 파일 업로드 중 오류 작업 실패:", file_error)
        return

    with sync_session() as db:
        try:
            new_video = Video(
                user_id=user_id,
                organization_id=organization_id,
                title=title,
                description=description,
                path=dest_path,
            )
            db.add(new_video)
            db.commit()
            db.refresh(new_video)
            print(f"[UPDATED] Video {new_video.id} 업로드 완료")

        except Exception as e:
            db.rollback()
            print("[ERROR] Video 업로드 작업 실패:", e)


@celery_app.task(name="process_video_update")
def process_video_update(payload: dict):
    """영상 업데이트 비동기 로직"""

    video_id = payload["video_id"]
    title = payload.get("title")
    description = payload.get("description")
    organization_id = payload["organization_id"]
    tmp_path = payload.get("tmp_path")
    new_path = None

    try:
        if tmp_path:
            new_path = upload_video_file(tmp_path, organization_id)
    except Exception as file_error:
        print("[ERROR] 파일 업로드 중 오류 작업 실패:", file_error)
        return

    try:
        with sync_session() as db:
            video = db.execute(
                select(Video).where(
                    and_(Video.id == video_id, Video.is_deleted.is_(False))
                )
            ).scalar()

            if video is not None:
                if new_path:
                    video.path = new_path
                if title:
                    video.title = title
                if description:
                    video.description = description

                db.commit()
                print(f"[UPDATED] Video {video_id} 업데이트 완료")

    except SQLAlchemyError as e:
        db.rollback()
        print("[ERROR] Video DB 업데이트 실패 :", e)
