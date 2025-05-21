from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.db.base import Base, TimestampModel


class User(Base, TimestampModel):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("organization_id", "email", name="unique_organization_email"),
    )

    id = Column(BigInteger, primary_key=True, index=True)
    organization_id = Column(
        BigInteger, ForeignKey("organizations.id"), nullable=False, index=True
    )
    email = Column(String, nullable=False, index=True, doc="유저 이메일")
    hashed_password = Column(String, nullable=False, doc=" 비밀번호")
    is_admin = Column(Boolean, default=False, doc="어드민 여부")
    joined_at = Column(
        DateTime, server_default=func.now(), nullable=False, doc="가입일"
    )
    deactivated_at = Column(DateTime, nullable=True, doc="탈퇴일")
    is_active = Column(Boolean, default=True, nullable=False, doc="활성화 여부")

    organization = relationship("Organization", backref="users")

    is_paid: bool = False  # organization 이용 중인 플랜 유료 여부 판별

    def set_password(self, raw_password: str):
        """비밀번호 암호화"""
        from src.auth.serivce import hash_password

        self.hashed_password = hash_password(raw_password)

    def verify_password(self, raw_password: str) -> bool:
        """비밀번호 검증"""
        from src.auth.serivce import verify_password

        return verify_password(raw_password, self.hashed_password)


class UserVideoPoint(Base, TimestampModel):
    __tablename__ = "user_video_points"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    video_id = Column(BigInteger, ForeignKey("videos.id"), nullable=False, index=True)
    point = Column(Integer, nullable=False, default=10, doc="포인트")

    user = relationship("User", backref="points")
    video = relationship("Video", backref="points")
