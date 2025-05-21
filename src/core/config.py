import os

from aioredlock import Aioredlock
from dotenv import load_dotenv

load_dotenv()

# DB
DATABASE_URL = os.getenv("ASYNC_DATABASE_URL")
SYNC_DATABASE_URL = os.getenv("SYNC_DATABASE_URL")

# Token
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_WEEKS = int(os.getenv("ACCESS_TOKEN_EXPIRE_WEEKS"))
REFRESH_TOKEN_EXPIRE_WEEKS = int(os.getenv("REFRESH_TOKEN_EXPIRE_WEEKS"))

# Static
TEMP_UPLOAD_DIR = os.getenv("TEMP_UPLOAD_DIR")
UPLOAD_DIR = os.getenv("UPLOAD_DIR")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1048576"))  # 1MB 기본값

# Redis
REDIS_HOST_1 = os.getenv("REDIS_HOST_1", "localhost")
REDIS_HOST_2 = os.getenv("REDIS_HOST_2", None)
REDIS_HOST_3 = os.getenv("REDIS_HOST_3", None)
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
LOCK_MANAGER = Aioredlock(
    [
        {"host": REDIS_HOST_1, "port": REDIS_PORT},
        {"host": REDIS_HOST_2, "port": REDIS_PORT},
        {"host": REDIS_HOST_3, "port": REDIS_PORT},
    ],
    retry_count=1,
)
