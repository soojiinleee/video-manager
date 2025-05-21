from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.auth.permissions import admin_required
from src.organization.schemas import (
    OrganizationCreate,
    PaidSubscriptionRead,
)
from src.organization import service as org_svc
from src.user.models import User
from src.organization import exceptions
from src.core.schemas import ErrorResponse

router = APIRouter(prefix="/organization", tags=["organization"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="기업 생성",
    responses={
        status.HTTP_409_CONFLICT: {
            "model": ErrorResponse,
            "description": exceptions.DuplicateOrganizationName().detail,
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ErrorResponse,
            "description": exceptions.OrganizationCreateFailed().detail,
        },
    },
)
async def create_organization(
    data: OrganizationCreate, db: AsyncSession = Depends(get_db)
):
    """
    기업 등록 및 초기 어드민 계정 생성

    - **name** : 기업명
    - **email** : 어드민 이메일
    - **password** : 어드민 비밀번호
    """
    return await org_svc.create_organization_all(db=db, data=data)


@router.post(
    "/paid",
    status_code=status.HTTP_201_CREATED,
    response_model=PaidSubscriptionRead,
    summary="유료 구독 전환",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorResponse,
            "description": "관리자 권한이 필요합니다.",
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ErrorResponse,
            "description": exceptions.SubscriptionCreateFailed().detail,
        },
    },
)
async def create_paid_subscription(
    current_user: User = Depends(admin_required),
):
    """
    유료 구독 전환

    - 토큰 필수
    - 어드민 계정만 접근 가능
    """

    new_subscription = await org_svc.switch_to_paid_plan(
        org_id=current_user.organization_id
    )
    return PaidSubscriptionRead.model_validate(new_subscription)
