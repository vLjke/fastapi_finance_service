"""FastAPI application with auth, wallets, transactions, and finance logic."""

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import Transaction, User, Wallet
from app.schemas import (
    SavingPlanItem,
    SavingPlanResponse,
    Token,
    TransactionCreate,
    TransactionOut,
    TransactionUpdate,
    UserCreate,
    UserOut,
    WalletCreate,
    WalletOut,
    WalletUpdate,
)
from app.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)

app = FastAPI(title="Personal Finance & Budget Service", version="1.0.0")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
Base.metadata.create_all(bind=engine)


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    """Resolve authenticated user from JWT bearer token."""
    username = decode_access_token(token)
    user = db.query(User).filter(User.username == username).first() if username else None
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return user


@app.post("/auth/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    """Create a new user account."""
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )
    user = User(username=payload.username, hashed_password=get_password_hash(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> Token:
    """Authenticate user and return JWT token."""
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    return Token(access_token=create_access_token(subject=user.username), token_type="bearer")


@app.get("/users/me", response_model=UserOut)
def read_me(current_user: User = Depends(get_current_user)) -> User:
    """Return profile data for currently authenticated user."""
    return current_user
