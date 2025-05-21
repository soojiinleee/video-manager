from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from src.core.config import DATABASE_URL


# 비동기 db 연결
async_engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(
    bind=async_engine,
    autocommit=False,
    autoflush=False,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    db = async_session()
    try:
        yield db
    finally:
        await db.close()


async def get_transaction_db() -> AsyncSession:
    """트랜잭션용 세션"""
    return async_session()
