"""Pydantic schemas for request validation and API responses."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class Token(BaseModel):
    """JWT token response schema."""

    access_token: str
    token_type: str


class UserCreate(BaseModel):
    """User registration payload."""

    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=100)


class UserOut(BaseModel):
    """Public user representation."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    is_active: bool


class WalletBase(BaseModel):
    """Base wallet fields."""

    name: str = Field(min_length=2, max_length=100)
    balance: float = Field(ge=0)


class WalletCreate(WalletBase):
    """Wallet creation payload."""


class WalletUpdate(BaseModel):
    """Partial wallet update payload."""

    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    balance: Optional[float] = Field(default=None, ge=0)


class WalletOut(WalletBase):
    """Wallet response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
