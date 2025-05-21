from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_serializer
from typing import Annotated, Optional


class VideoRead(BaseModel):
    id: Annotated[int, Field(description="영상 ID", example=1)]
    title: Annotated[str, Field(description="영상 제목", exmaple="Video_1")]
    description: Annotated[
        str, Field(None, description="영상 설명", example="Video Description")
    ]
    path: Annotated[
        Optional[str], Field(None, description="영상 경로", example="./upload/")
    ]
    created_at: Annotated[datetime, Field(description="최초 업로드 일시")]

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("created_at")
    def serialize_datetime(self, value: datetime, _info):
        return value.strftime("%Y-%m-%d %H:%M")
