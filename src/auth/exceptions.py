from src.core.exceptions import UnauthorizedException


class InvalidCredentials(UnauthorizedException):
    def __init__(self):
        super().__init__("이메일 또는 비밀번호가 올바르지 않습니다.")
