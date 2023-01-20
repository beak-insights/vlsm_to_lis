from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from logger import Logger

from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST

logger = Logger(__name__, __file__)


async_engine = create_async_engine(
    f"mysql+asyncmy://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}?charset=utf8mb4",
    pool_pre_ping=True, echo=False, future=True
)
async_session_factory = sessionmaker(
    bind=async_engine, expire_on_commit=False, autoflush=False, class_=AsyncSession
)


async def test_db_connection() -> bool:
    try:
        async with async_session_factory() as session:
            result = await session.execute(text("""select * from orders limit 1"""))
        logger.log("info", f"HL7DB: connection established")
        return True
    except Exception as e:
        logger.log("error", f"HL7DB: connection failed with error: {e}")
        return False
