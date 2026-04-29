"""SQLAlchemy ORM models for users, wallets, and transactions."""

from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    """Application user model."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    wallets = relationship("Wallet", back_populates="owner", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="owner", cascade="all, delete-orphan")
