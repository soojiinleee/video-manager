from src.core.exceptions import (
    AppBaseException,
    NotFoundException,
    DuplicateDataException,
)
from fastapi import status


class DuplicateOrganizationName(DuplicateDataException):
    def __init__(self):
        super().__init__(
            "이미 등록된 기업명 입니다.",
        )


class OrganizationCreateFailed(AppBaseException):
    def __init__(self):
        super().__init__(
            detail="조직 생성 및 어드민 계정 추가에 실패했습니다.",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


class SubscriptionCreateFailed(AppBaseException):
    def __init__(self):
        super().__init__(
            detail="유료 구독 전환 실패했습니다.",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


class PlanNotFound(NotFoundException):
    def __init__(self):
        super().__init__("구독 플랜이 존재하지 않습니다.")
