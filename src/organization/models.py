from datetime import datetime, timedelta
from sqlalchemy import (
    Column,
    BigInteger,
    String,
    DateTime,
    Integer,
    Boolean,
    Text,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.db.base import Base, TimestampModel


class Organization(Base, TimestampModel):
    __tablename__ = "organizations"

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, doc="기업 이름")


class OrganizationPlan(Base, TimestampModel):
    __tablename__ = "organization_plans"

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(50), nullable=False, doc="기업 플랜 이름")
    description = Column(Text, nullable=True, doc="기업 플랜 설명")
    price = Column(Integer, default=0, doc="가격, 0이면 무료 플랜")
    duration = Column(
        Integer, nullable=True, doc="플랜 구독 기간(day(일) 단위), Null이면 무료 플랜"
    )
    recoverable = Column(Boolean, default=False, doc="삭제 영상 복구 여부")


class OrganizationSubscription(Base, TimestampModel):
    __tablename__ = "organization_subscriptions"

    id = Column(BigInteger, primary_key=True, index=True)
    organization_id = Column(BigInteger, ForeignKey("organizations.id"), nullable=False)
    plan_id = Column(BigInteger, ForeignKey("organization_plans.id"), nullable=False)
    start_date = Column(DateTime, nullable=False, default=func.now(), doc="구독 시작일")
    end_date = Column(DateTime, nullable=True, doc="구독 만료일")
    is_active = Column(Boolean, default=True, doc="현재 활성화 여부")

    organization = relationship("Organization", backref="subscriptions")
    plan = relationship("OrganizationPlan", backref="subscriptions")

    @classmethod
    def create_from_plan(cls, org_id: int, plan: OrganizationPlan):
        """플랜 정보를 기반으로 구독 인스턴스 생성 (end_date 계산 포함)"""

        end_date = None
        if plan.duration:
            end_date = datetime.now() + timedelta(days=plan.duration)

        return cls(
            organization_id=org_id,
            plan_id=plan.id,
            end_date=end_date,
        )
