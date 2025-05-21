from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.config import SYNC_DATABASE_URL

sync_engine = create_engine(SYNC_DATABASE_URL, echo=True)
sync_session = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)
