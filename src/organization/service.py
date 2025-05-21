from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.db.session import get_transaction_db
from src.organization.schemas import OrganizationCreate, PlanType
from src.organization import exceptions

from src.organization import repository as org_repo
from src.user.repository import create_admin_user


async def is_organization_exists(db: AsyncSession, name: str):
    """기업 이름 중복 검사"""

    organization = await org_repo.get_organization_by_name(db=db, name=name)

    if organization:
        raise exceptions.DuplicateOrganizationName


async def create_organization_all(db: AsyncSession, data: OrganizationCreate):
    """기업 + 어드민 + 구독 생성 트랜잭션"""

    try:
        async with db.begin():
            # 1. 조직 생성
            org = await org_repo.create_organization(db, data.name)

            # 2. 어드민 생성
            await create_admin_user(db, org.id, data.email, data.password)

            # 3. 무료 구독 플랜 조회 및 구독 생성
            trial_plan = await org_repo.get_subscription_plan_by_name(
                db, PlanType.TRIAL.value
            )
            await org_repo.create_trial_subscription(db, org.id, trial_plan)

            return org

    except SQLAlchemyError:
        raise exceptions.OrganizationCreateFailed


async def switch_to_paid_plan(
    org_id: int,
    plan_name: str = PlanType.PAID.value,
):
    """유료 플랜 전환 : 무료 구독 만료 -> 유료 구독 생성 (트랜잭션)"""

    db = await get_transaction_db()

    try:
        async with db.begin():
            # 1. 무료 구독 종료
            await org_repo.expire_subscription(db=db, org_id=org_id)

            # 2. 유료 구독 생성
            plan = await org_repo.get_subscription_plan_by_name(db=db, name=plan_name)
            new_sub = await org_repo.create_paid_subscription(
                db=db, org_id=org_id, plan=plan
            )
            print("*" * 10, type(new_sub), new_sub)
            print(new_sub.start_date, new_sub.end_date)
            return new_sub

    except SQLAlchemyError:
        raise exceptions.SubscriptionCreateFailed
