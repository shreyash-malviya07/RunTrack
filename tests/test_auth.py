import os
import pytest
from fastapi.testclient import TestClient
from database.connection import Base, engine, SessionLocal
from backend.main import app

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup runs and users after test
    db = SessionLocal()
    try:
        from database.models import User
        db.query(User).filter(User.username.like("testuser_%")).delete(synchronize_session=False)
        db.commit()
    finally:
        db.close()


def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_register_and_login_flow():
    username = "testuser_runner1"
    email = "runner1@example.com"
    password = "SecurePassword123!"

    # 1. Register
    reg_payload = {
        "email": email,
        "username": username,
        "full_name": "Test Runner One",
        "password": password,
    }
    reg_resp = client.post("/auth/register", json=reg_payload)
    assert reg_resp.status_code == 201, reg_resp.text
    reg_data = reg_resp.json()
    assert "access_token" in reg_data
    assert reg_data["user"]["username"] == username
    token = reg_data["access_token"]

    # 2. Access /auth/me with Bearer token
    me_resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["username"] == username
    assert me_data["email"] == email

    # 3. Duplicate registration should fail
    dup_resp = client.post("/auth/register", json=reg_payload)
    assert dup_resp.status_code == 400

    # 4. Login with username
    login_resp = client.post("/auth/login", json={"username_or_email": username, "password": password})
    assert login_resp.status_code == 200
    assert "access_token" in login_resp.json()

    # 5. Login with invalid password should fail
    bad_login_resp = client.post("/auth/login", json={"username_or_email": username, "password": "WrongPassword"})
    assert bad_login_resp.status_code == 401


def test_unauthorized_access():
    response = client.get("/auth/me")
    assert response.status_code == 401
