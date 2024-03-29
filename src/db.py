from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy import text
from logger import Logger

from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST

logger = Logger(__name__, __file__)

db_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}?charset=utf8mb4"
engine = create_engine(
    db_url,
    pool_pre_ping=True, echo=False, future=True
)


def test_db_connection() -> bool:
    logger.log(
        "info", f"HL7DB: intiating connection: {db_url.replace(DB_PASSWORD, '******').replace(DB_USER, '******')}")
    try:
        with Session(engine) as session:
            result = session.execute(text("""select * from orders limit 1"""))
        logger.log("info", f"HL7DB: connection established")
        return True
    except Exception as e:
        logger.log("error", f"HL7DB: connection failed with error: {e}")
        return False
