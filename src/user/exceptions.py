from fastapi import status
from src.core.exceptions import (
    AppBaseException,
    ForbiddenException,
    NotFoundException,
    DuplicateDataException,
)


class InvalidCredentials(DuplicateDataException):
    def __init__(self):
        super().__init__("이메일 또는 비밀번호가 올바르지 않습니다.")


class UserNotFoundException(NotFoundException):
    def __init__(self):
        super().__init__("존재하지 않는 유저 id입니다.")


class UnauthorizedAccessException(ForbiddenException):
    def __init__(self):
        super().__init__("해당 유저에 대한 권한이 없습니다.")


class AddPointException(AppBaseException):
    def __init__(self):
        super().__init__(
            detail="잠시 후 다시 시도하세요.",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )
