from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def auth_headers(username: str = "alice", password: str = "password123") -> dict[str, str]:
    client.post("/auth/register", json={"username": username, "password": password})
    login_resp = client.post("/auth/login", data={"username": username, "password": password})
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_register_and_login():
    response = client.post("/auth/register", json={"username": "bob", "password": "password123"})
    assert response.status_code == 201
    assert response.json()["username"] == "bob"

    login_response = client.post("/auth/login", data={"username": "bob", "password": "password123"})
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()


def test_wallet_and_transaction_crud_flow():
    headers = auth_headers("charlie", "password123")

    wallet_resp = client.post("/wallets", json={"name": "Main card", "balance": 1000}, headers=headers)
    assert wallet_resp.status_code == 201
    wallet_id = wallet_resp.json()["id"]

    tx_resp = client.post(
        "/transactions",
        json={
            "amount": 150.0,
            "type": "expense",
            "category": "Groceries",
            "note": "Weekly shop",
            "month": "2026-04",
            "is_planned": False,
            "wallet_id": wallet_id,
        },
        headers=headers,
    )
    assert tx_resp.status_code == 201
    transaction_id = tx_resp.json()["id"]

    get_tx_resp = client.get(f"/transactions/{transaction_id}", headers=headers)
    assert get_tx_resp.status_code == 200
    assert get_tx_resp.json()["amount"] == 150.0

    update_tx_resp = client.put(
        f"/transactions/{transaction_id}",
        json={"amount": 120.0, "note": "Discounted shop"},
        headers=headers,
    )
    assert update_tx_resp.status_code == 200
    assert update_tx_resp.json()["amount"] == 120.0

    delete_tx_resp = client.delete(f"/transactions/{transaction_id}", headers=headers)
    assert delete_tx_resp.status_code == 204


def test_savings_plan_endpoint():
    headers = auth_headers("diana", "password123")

    wallet_resp = client.post("/wallets", json={"name": "Cash", "balance": 2000}, headers=headers)
    wallet_id = wallet_resp.json()["id"]

    tx_payload = [
        {"amount": 200, "type": "expense", "category": "Food", "note": "Food", "month": "2026-04", "wallet_id": wallet_id},
        {"amount": 350, "type": "expense", "category": "Cafe", "note": "Cafe", "month": "2026-04", "wallet_id": wallet_id},
        {"amount": 100, "type": "expense", "category": "Food", "note": "Food2", "month": "2026-04", "wallet_id": wallet_id},
    ]
    for payload in tx_payload:
        create_resp = client.post("/transactions", json=payload, headers=headers)
        assert create_resp.status_code == 201

    plan_resp = client.get("/finance/savings-plan?month=2026-04&saving_target=300", headers=headers)
    assert plan_resp.status_code == 200
    body = plan_resp.json()
    assert body["total_reducible"] >= 300
    assert len(body["selected_reductions"]) >= 1
