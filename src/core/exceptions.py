from fastapi import HTTPException, status


class AppBaseException(HTTPException):
    """모든 커스텀 예외의 부모 클래스"""

    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class InternalServerErrorException(AppBaseException):
    def __init__(self, detail: str = "서버 내부 오류가 발생했습니다."):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail
        )


class UnauthorizedException(AppBaseException):
    def __init__(self, detail="인증이 필요합니다."):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)


class ForbiddenException(AppBaseException):
    def __init__(self, detail="접근 권한이 없습니다."):
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN)


class NotFoundException(AppBaseException):
    def __init__(self, detail="요청한 리소스를 찾을 수 없습니다."):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)


class DuplicateDataException(AppBaseException):
    def __init__(self, detail="중복된 데이터 입니다."):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_409_CONFLICT,
        )
