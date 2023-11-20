from contextvars import ContextVar

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from app.core.settings import settings


def get_uri():
    return settings.DATABASE_URL.replace("postgres", "postgresql")


engine = create_engine(get_uri())

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


db_session: ContextVar[Session] = ContextVar("db_session")
