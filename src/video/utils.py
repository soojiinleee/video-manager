import aiofiles as aio
import os
import shutil
import time
import uuid

from fastapi import UploadFile
from typing import AsyncGenerator

from src.core.config import TEMP_UPLOAD_DIR, UPLOAD_DIR, CHUNK_SIZE
from src.video import exceptions as video_exceptions


async def save_temp_file(file: UploadFile) -> str:
    """임시 저장"""
    if not os.path.exists(TEMP_UPLOAD_DIR):
        os.makedirs(TEMP_UPLOAD_DIR)

    ext = os.path.splitext(file.filename)[1]
    tmp_filename = f"{uuid.uuid4().hex}_{ext}"
    tmp_path = os.path.join(TEMP_UPLOAD_DIR, tmp_filename)

    async with aio.open(tmp_path, "wb") as out_file:
        while chunk := await file.read(1024):
            await out_file.write(chunk)

    return tmp_path


def upload_video_file(tmp_path: str, organization_id: int) -> str:
    """영상 파일 업로드"""
    try:
        filename = os.path.basename(tmp_path)
        org_dir = os.path.join(UPLOAD_DIR, f"{organization_id}")
        if not os.path.exists(org_dir):
            os.makedirs(org_dir)

        dest_path = os.path.join(org_dir, f"{int(time.time())}_{filename}")
        shutil.move(tmp_path, dest_path)

        return dest_path

    except Exception as e:
        print("[ERROR]", e)
        raise video_exceptions.VideoUploadException


async def stream_video(video_path: str) -> AsyncGenerator[bytes, None]:
    """비디오 파일을 스트리밍으로 읽어오는 Generator"""

    try:
        async with aio.open(video_path, "rb") as video_file:
            while chunk := await video_file.read(CHUNK_SIZE):
                yield chunk

    except Exception as e:
        print("[ERROR]", e)
        raise video_exceptions.VideoStreamingException
