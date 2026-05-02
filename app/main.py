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


@app.post("/wallets", response_model=WalletOut, status_code=status.HTTP_201_CREATED)
def create_wallet(
    payload: WalletCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Wallet:
    """Create wallet for authenticated user."""
    wallet = Wallet(name=payload.name, balance=payload.balance, owner_id=current_user.id)
    db.add(wallet)
    db.commit()
    db.refresh(wallet)
    return wallet


@app.get("/wallets", response_model=list[WalletOut])
def list_wallets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Wallet]:
    """List wallets owned by authenticated user."""
    return db.query(Wallet).filter(Wallet.owner_id == current_user.id).all()


@app.get("/wallets/{wallet_id}", response_model=WalletOut)
def get_wallet(
    wallet_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Wallet:
    """Get one wallet by id for authenticated user."""
    wallet = (
        db.query(Wallet)
        .filter(Wallet.id == wallet_id, Wallet.owner_id == current_user.id)
        .first()
    )
    if not wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")
    return wallet


@app.put("/wallets/{wallet_id}", response_model=WalletOut)
def update_wallet(
    wallet_id: int,
    payload: WalletUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Wallet:
    """Update wallet fields for authenticated user."""
    wallet = (
        db.query(Wallet)
        .filter(Wallet.id == wallet_id, Wallet.owner_id == current_user.id)
        .first()
    )
    if not wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(wallet, field, value)
    db.commit()
    db.refresh(wallet)
    return wallet


@app.delete("/wallets/{wallet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_wallet(
    wallet_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete wallet by id for authenticated user."""
    wallet = (
        db.query(Wallet)
        .filter(Wallet.id == wallet_id, Wallet.owner_id == current_user.id)
        .first()
    )
    if not wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")
    db.delete(wallet)
    db.commit()


@app.post("/transactions", response_model=TransactionOut, status_code=status.HTTP_201_CREATED)
def create_transaction(
    payload: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Transaction:
    """Create transaction and update related wallet balance."""
    wallet = (
        db.query(Wallet)
        .filter(Wallet.id == payload.wallet_id, Wallet.owner_id == current_user.id)
        .first()
    )
    if not wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")
    transaction = Transaction(**payload.model_dump(), owner_id=current_user.id)
    wallet.balance += payload.amount if payload.type == "income" else -payload.amount
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


@app.get("/transactions", response_model=list[TransactionOut])
def list_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Transaction]:
    """List transactions for authenticated user."""
    return db.query(Transaction).filter(Transaction.owner_id == current_user.id).all()


@app.get("/transactions/{transaction_id}", response_model=TransactionOut)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Transaction:
    """Get one transaction by id for authenticated user."""
    transaction = (
        db.query(Transaction)
        .filter(Transaction.id == transaction_id, Transaction.owner_id == current_user.id)
        .first()
    )
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return transaction


@app.put("/transactions/{transaction_id}", response_model=TransactionOut)
def update_transaction(
    transaction_id: int,
    payload: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Transaction:
    """Update transaction fields for authenticated user."""
    transaction = (
        db.query(Transaction)
        .filter(Transaction.id == transaction_id, Transaction.owner_id == current_user.id)
        .first()
    )
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    data = payload.model_dump(exclude_unset=True)
    if "wallet_id" in data:
        wallet = (
            db.query(Wallet)
            .filter(Wallet.id == data["wallet_id"], Wallet.owner_id == current_user.id)
            .first()
        )
        if not wallet:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")
    for field, value in data.items():
        setattr(transaction, field, value)
    db.commit()
    db.refresh(transaction)
    return transaction


@app.delete("/transactions/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete transaction by id for authenticated user."""
    transaction = (
        db.query(Transaction)
        .filter(Transaction.id == transaction_id, Transaction.owner_id == current_user.id)
        .first()
    )
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    db.delete(transaction)
    db.commit()


@app.get("/finance/savings-plan", response_model=SavingPlanResponse)
def build_savings_plan(
    month: str,
    saving_target: float,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SavingPlanResponse:
    """Suggest biggest expenses to cut until reaching savings target."""
    if saving_target <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="saving_target must be positive",
        )
    expenses = (
        db.query(Transaction)
        .filter(
            Transaction.owner_id == current_user.id,
            Transaction.month == month,
            Transaction.type == "expense",
            Transaction.is_planned.is_(False),
        )
        .order_by(Transaction.amount.desc())
        .all()
    )
    total = 0.0
    selected: list[SavingPlanItem] = []
    for tx in expenses:
        if total >= saving_target:
            break
        selected.append(
            SavingPlanItem(
                transaction_id=tx.id,
                category=tx.category,
                amount=tx.amount,
                score=round(tx.amount, 2),
            )
        )
        total += tx.amount
    return SavingPlanResponse(
        month=month,
        saving_target=saving_target,
        total_reducible=round(total, 2),
        selected_reductions=selected,
    )
