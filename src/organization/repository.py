from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_

from src.organization import exceptions
from src.organization.models import (
    Organization,
    OrganizationPlan,
    OrganizationSubscription,
)


async def get_organization_by_name(db: AsyncSession, name: str):
    stmt = select(Organization).where(Organization.name == name)
    query = await db.execute(stmt)
    return query.scalar_one_or_none()


async def get_subscription_plan_by_name(
    db: AsyncSession, name: str
) -> OrganizationPlan:
    """기업 구독 플랜 조회"""

    stmt = select(OrganizationPlan).where(OrganizationPlan.name == name)
    query = await db.execute(stmt)
    plan = query.scalar()

    if not plan:
        raise exceptions.PlanNotFound

    return plan


async def create_organization(db: AsyncSession, name: str) -> Organization:
    new_org = Organization(name=name)
    db.add(new_org)
    await db.flush()

    return new_org


async def create_trial_subscription(
    db: AsyncSession, org_id: int, plan: OrganizationPlan
) -> OrganizationSubscription:
    """무료 구독 생성"""

    trial_sub = OrganizationSubscription.create_from_plan(org_id=org_id, plan=plan)
    db.add(trial_sub)
    await db.flush()

    return trial_sub


async def create_paid_subscription(
    db: AsyncSession, org_id: int, plan: OrganizationPlan
) -> OrganizationSubscription:
    """유료 구독 생성"""

    subscription = OrganizationSubscription.create_from_plan(org_id, plan)
    db.add(subscription)
    await db.flush()

    return subscription


async def expire_subscription(db: AsyncSession, org_id: int):
    """기존 구독 만료"""

    stmt = (
        update(OrganizationSubscription)
        .where(
            OrganizationSubscription.organization_id == org_id,
            OrganizationSubscription.is_active.is_(True),
        )
        .values(is_active=False, end_date=datetime.now())
    )
    await db.execute(stmt.execution_options(synchronize_session="fetch"))


async def is_paid_plan(db: AsyncSession, organization_id) -> bool:
    """
    유료 플랜 이용 여부 판별
    - 현재 활성화된 구독이 있고
    - 해당 플랜의 복구 가능이 true
    """
    stmt = (
        select(OrganizationSubscription)
        .join(OrganizationSubscription.plan)
        .where(
            and_(
                OrganizationSubscription.organization_id == organization_id,
                OrganizationSubscription.is_active.is_(True),
                OrganizationPlan.recoverable.is_(True),
            )
        )
    )
    query = await db.execute(stmt)
    subscription = query.scalar()

    return subscription is not None
