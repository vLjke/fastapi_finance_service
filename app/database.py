"""Database engine and session configuration."""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./finance_service.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SESSION_LOCAL = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SESSION_LOCAL()
    try:
        yield db
    finally:
        db.close()
