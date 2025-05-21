from sqlalchemy import Column, BigInteger, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from src.db.base import Base, TimestampModel


class Video(Base, TimestampModel):
    __tablename__ = "videos"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    organization_id = Column(
        BigInteger, ForeignKey("organizations.id"), nullable=False, index=True
    )
    title = Column(String(250), nullable=False, index=True, doc="영상 제목")
    description = Column(Text, nullable=False, doc="영상 설명")
    path = Column(String(300), nullable=True, doc="업로드 경로")
    is_deleted = Column(Boolean, default=False, nullable=False, doc="삭제 여부")
    deleted_at = Column(DateTime, nullable=True, doc="삭제일시")

    organization = relationship("Organization", backref="videos", lazy="raise")
    uploader = relationship("User", backref="videos", lazy="raise")
