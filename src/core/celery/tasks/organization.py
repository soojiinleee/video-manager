from datetime import datetime
from celery import shared_task
from sqlalchemy import select, update, and_
from sqlalchemy.exc import SQLAlchemyError

from src.db.sync_session import sync_session
from src.organization.models import OrganizationSubscription, OrganizationPlan


@shared_task(name="expire_paid_subscriptions")
def expire_paid_subscriptions():
    """만료 유료 플랜 비활성화 작업"""

    with sync_session() as db:
        now = datetime.now()
        try:
            with db.begin():
                # 1. 만료 대상 유료 구독 조회
                paid_subscription_stmt = (
                    select(OrganizationSubscription.organization_id)
                    .join(OrganizationSubscription.plan)
                    .where(
                        and_(
                            OrganizationSubscription.is_active.is_(True),
                            OrganizationSubscription.end_date <= now,
                            OrganizationPlan.price > 0,
                        )
                    )
                )
                query = db.execute(paid_subscription_stmt)
                expired_org_ids = [row.organization_id for row in query.fetchall()]

                # 2. 유료 구독 만료
                stmt = (
                    update(OrganizationSubscription)
                    .where(
                        and_(
                            OrganizationSubscription.is_active.is_(True),
                            OrganizationSubscription.end_date <= datetime.now(),
                        )
                    )
                    .values(is_active=False, end_date=now)
                )
                db.execute(stmt)

                # 2. 무료 구독 추가 -> 커밋
                plan_id = db.query(OrganizationPlan).filter(name="TRIAL").first().id
                subscriptions = [
                    OrganizationSubscription(
                        organization_id=org_id,
                        plan_id=plan_id,
                    )
                    for org_id in expired_org_ids
                ]
                db.add_all(subscriptions)
                db.commit()

                print(
                    f"[INFO] {len(expired_org_ids)}개 조직이 무료 플랜으로 전환 되었습니다."
                )

        except SQLAlchemyError as e:
            print("[ERROR] expire_paid_subscriptions >>> ", e)
