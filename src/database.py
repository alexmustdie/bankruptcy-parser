from datetime import datetime
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from src.config import config
from src.models import Base, FedresursData
from src.utils.logger import get_logger

logger = get_logger(__name__)


class Database:
    def __init__(self):
        self.engine = create_engine(
            config.DATABASE_URL, pool_pre_ping=True, pool_recycle=3600
        )
        self.SessionLocal = sessionmaker(
            bind=self.engine, autocommit=False, autoflush=False
        )
        self.init_db()

    def init_db(self):
        Base.metadata.create_all(bind=self.engine)
        logger.info(f"Database initialized: {config.DATABASE_URL}")

    @contextmanager
    def get_session(self) -> Session:
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            session.close()

    def get_processed_inns(self) -> set:
        try:
            with self.get_session() as session:
                processed = session.query(FedresursData.inn).all()
                return {row[0] for row in processed}
        except SQLAlchemyError as e:
            logger.error(f"Failed to get processed INNs: {e}")
            return set()

    @staticmethod
    def parse_date(date_str: str):
        if not date_str:
            return None
        try:
            if "." in date_str:
                return datetime.strptime(date_str, "%d.%m.%Y")
            elif "-" in date_str:
                return datetime.strptime(date_str, "%Y-%m-%d")
        except (ValueError, TypeError):
            logger.warning(f"Could not parse date: {date_str}")
        return None

    def close(self):
        self.engine.dispose()


db = Database()
