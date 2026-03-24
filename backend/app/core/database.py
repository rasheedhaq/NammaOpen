from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import get_settings

settings = get_settings()
DEFAULT_SQLITE_PATH = Path(__file__).resolve().parents[2] / "nammaopen.db"

DATABASE_URL = settings.database_url or (
    f"sqlite:///{DEFAULT_SQLITE_PATH.as_posix()}"
)

engine_kwargs = {"echo": False, "future": True, "pool_pre_ping": True}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
