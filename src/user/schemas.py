from enum import Enum
from pydantic import BaseModel, EmailStr, Field
from typing import Annotated, Optional

from src.user.models import User


class RoleType(str, Enum):
    """유저 타입"""

    ADMIN = "admin"
    GUEST = "guest"


class UserCredential(BaseModel):
    """로그인 입력 정보"""

    organization_id: Annotated[int, Field(..., description="기업 id", example=1)]
    email: Annotated[
        EmailStr, Field(..., description="이메일", example="org1@example.com")
    ]
    password: Annotated[
        str, Field(..., description="비밀번호", example="org1@example.com")
    ]


class UserCreate(BaseModel):
    email: Annotated[
        EmailStr, Field(..., description="이메일", example="user1@example.com")
    ]
    password: Annotated[
        Optional[str],
        Field(None, description="비밀번호", example="user1@example.com"),
    ]


class UserRead(BaseModel):
    id: Annotated[int, Field(..., description="유저 id", example=2)]
    email: Annotated[
        EmailStr, Field(..., description="계정", example="user1@example.com")
    ]
    organization_name: Annotated[
        Optional[str], Field(None, description="소속 기업", example="org1")
    ]
    role: Annotated[str, Field(description="역할", example="guest")]

    @classmethod
    def from_orm(cls, user: User):
        role = RoleType.ADMIN.value if user.is_admin else RoleType.GUEST.value

        return cls(
            id=user.id,
            email=user.email,
            organization_name=user.organization.name if user.organization else None,
            role=role,
        )


class PasswordUpdate(BaseModel):
    new_password: Annotated[
        Optional[str],
        Field(None, description="새 비밀번호", example="password123!@#"),
    ]


class AdminUserUpdate(PasswordUpdate):
    is_admin: Annotated[
        Optional[bool], Field(None, description="어드민 권한 여부", example=True)
    ]
