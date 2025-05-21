from src.core.exceptions import (
    ForbiddenException,
    NotFoundException,
    InternalServerErrorException,
)


class VideoNotFoundException(NotFoundException):
    def __init__(self):
        super().__init__("영상을 찾을 수 없습니다.")


class UnauthorizedAccessException(ForbiddenException):
    def __init__(self):
        super().__init__("영상에 대한 권한이 없습니다.")


class VideoUpdateFailedException(InternalServerErrorException):
    def __init__(self):
        super().__init__("영상 정보 업데이트 중 오류가 발생했습니다.")


class VideoRestoreFailedException(InternalServerErrorException):
    def __init__(self):
        super().__init__("영상 복구 중 오류가 발생했습니다.")


class VideoDeleteFailedException(InternalServerErrorException):
    def __init__(self):
        super().__init__("영상 삭제 중 오류가 발생했습니다.")


class VideoUploadException(InternalServerErrorException):
    def __init__(self):
        super().__init__("영상 업로드 중 오류가 발생했습니다.")


class VideoStreamingException(InternalServerErrorException):
    def __init__(self):
        super().__init__("영상 재생 중 오류가 발생했습니다.")
