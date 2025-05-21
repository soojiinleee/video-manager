from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from src.auth.exceptions import InvalidCredentials

from src.user.models import User
from src.user.schemas import UserCredential
from src.user.repository import get_active_user_by_email_and_org


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def authenticate_user(db: AsyncSession, data: UserCredential) -> User:
    user = await get_active_user_by_email_and_org(
        db, email=data.email, organization_id=data.organization_id
    )

    if not user or not verify_password(data.password, user.hashed_password):
        raise InvalidCredentials

    return user
