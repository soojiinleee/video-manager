from sqlalchemy import Column, DateTime
from sqlalchemy.orm import declarative_base, declarative_mixin
from sqlalchemy.sql import func

Base = declarative_base()


@declarative_mixin
class TimestampModel:
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
