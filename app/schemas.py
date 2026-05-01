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


class TransactionBase(BaseModel):
    """Base transaction fields."""

    amount: float = Field(gt=0)
    type: str = Field(pattern="^(income|expense)$")
    category: str = Field(min_length=2, max_length=100)
    note: Optional[str] = Field(default=None, max_length=300)
    month: str = Field(pattern=r"^\d{4}-(0[1-9]|1[0-2])$")
    is_planned: bool = False
    wallet_id: int


class TransactionCreate(TransactionBase):
    """Transaction creation payload."""


class TransactionUpdate(BaseModel):
    """Partial transaction update payload."""

    amount: Optional[float] = Field(default=None, gt=0)
    type: Optional[str] = Field(default=None, pattern="^(income|expense)$")
    category: Optional[str] = Field(default=None, min_length=2, max_length=100)
    note: Optional[str] = Field(default=None, max_length=300)
    month: Optional[str] = Field(default=None, pattern=r"^\d{4}-(0[1-9]|1[0-2])$")
    is_planned: Optional[bool] = None
    wallet_id: Optional[int] = None


class TransactionOut(BaseModel):
    """Transaction response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    amount: float
    type: str
    category: str
    note: Optional[str]
    month: str
    is_planned: bool
    owner_id: int
    wallet_id: int


class SavingPlanItem(BaseModel):
    """Single expense candidate for savings reduction."""

    transaction_id: int
    category: str
    amount: float
    score: float


class SavingPlanResponse(BaseModel):
    """Savings plan response payload."""

    month: str
    saving_target: float
    total_reducible: float
    selected_reductions: list[SavingPlanItem]
