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


class Wallet(Base):
    """Wallet that belongs to a user."""

    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    balance = Column(Float, nullable=False, default=0.0)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    owner = relationship("User", back_populates="wallets")
    transactions = relationship(
        "Transaction",
        back_populates="wallet",
        cascade="all, delete-orphan",
    )


class Transaction(Base):
    """Income or expense transaction for a wallet."""

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    type = Column(String(10), nullable=False)  # income or expense
    category = Column(String(100), nullable=False)
    note = Column(String(300), nullable=True)
    month = Column(String(7), nullable=False)  # YYYY-MM
    is_planned = Column(Boolean, default=False, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    wallet_id = Column(Integer, ForeignKey("wallets.id", ondelete="CASCADE"), nullable=False)

    owner = relationship("User", back_populates="transactions")
    wallet = relationship("Wallet", back_populates="transactions")
