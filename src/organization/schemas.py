from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_serializer
from typing import Annotated
from enum import Enum


class PlanType(str, Enum):
    TRIAL = "TRIAL"
    PAID = "PAID"


class OrganizationCreate(BaseModel):
    name: Annotated[str, Field(..., description="기업 이름", example="org1")]
    email: Annotated[
        EmailStr,
        Field(..., description="어드민 계정 이메일", example="org1@example.com"),
    ]
    password: Annotated[
        str, Field(..., description="어드민 계정 비밀번호", example="org1")
    ]


class PaidSubscriptionRead(BaseModel):
    start_date: Annotated[
        datetime, Field(description="유료 구독 시작일시", example="2025-05-16 11:09")
    ]
    end_date: Annotated[
        datetime, Field(description="유료 구독 만료일시", example="2025-05-31 02:09")
    ]

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("start_date", "end_date")
    def serialize_datetime(self, value: datetime, _info):
        return value.strftime("%Y-%m-%d %H:%M")
