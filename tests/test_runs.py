from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient
from database.connection import Base, engine, SessionLocal
from database.models import User, Run
from backend.main import app

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_runs_db():
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup test users and their cascade runs
    db = SessionLocal()
    try:
        db.query(User).filter(User.username.like("runtest_%")).delete(synchronize_session=False)
        db.commit()
    finally:
        db.close()


def create_test_user(username: str, email: str) -> str:
    """Helper to register and obtain token."""
    res = client.post("/auth/register", json={
        "username": username,
        "email": email,
        "password": "Password123!",
        "full_name": f"Full {username}"
    })
    assert res.status_code == 201
    return res.json()["access_token"]


def test_runs_crud_and_user_isolation():
    # Setup two separate users
    token_a = create_test_user("runtest_alice", "alice@runtest.com")
    token_b = create_test_user("runtest_bob", "bob@runtest.com")

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 1. Alice creates a 10km run in 50 minutes (Pace should be 5.0 min/km)
    run_payload = {
        "date": "2026-10-01T08:00:00Z",
        "distance_km": 10.0,
        "duration_minutes": 50.0,
        "calories": 650,
        "avg_heart_rate": 152,
        "elevation_gain": 45.0,
        "notes": "Morning tempo run"
    }
    create_resp = client.post("/runs", json=run_payload, headers=headers_a)
    assert create_resp.status_code == 201, create_resp.text
    run_a = create_resp.json()
    assert run_a["pace_min_per_km"] == 5.0
    run_a_id = run_a["id"]

    # 2. Bob lists his runs: should NOT see Alice's run
    bob_runs_resp = client.get("/runs", headers=headers_b)
    assert bob_runs_resp.status_code == 200
    bob_runs = bob_runs_resp.json()
    assert len(bob_runs) == 0

    # 3. Bob attempts to access Alice's run directly: should receive 404
    bob_get_resp = client.get(f"/runs/{run_a_id}", headers=headers_b)
    assert bob_get_resp.status_code == 404

    # 4. Bob attempts to edit Alice's run: should receive 404
    bob_put_resp = client.put(f"/runs/{run_a_id}", json={"distance_km": 15.0}, headers=headers_b)
    assert bob_put_resp.status_code == 404

    # 5. Bob attempts to delete Alice's run: should receive 404
    bob_del_resp = client.delete(f"/runs/{run_a_id}", headers=headers_b)
    assert bob_del_resp.status_code == 404

    # 6. Alice edits her run: distance to 12.5km, pace should update to 50 / 12.5 = 4.0
    alice_update_resp = client.put(
        f"/runs/{run_a_id}",
        json={"distance_km": 12.5},
        headers=headers_a
    )
    assert alice_update_resp.status_code == 200
    assert alice_update_resp.json()["distance_km"] == 12.5
    assert alice_update_resp.json()["pace_min_per_km"] == 4.0

    # 7. Alice lists her runs
    alice_runs_resp = client.get("/runs", headers=headers_a)
    assert alice_runs_resp.status_code == 200
    assert len(alice_runs_resp.json()) == 1

    # 8. Alice deletes her run
    alice_del_resp = client.delete(f"/runs/{run_a_id}", headers=headers_a)
    assert alice_del_resp.status_code == 204

    # 9. Verifying it is gone
    alice_verify_resp = client.get(f"/runs/{run_a_id}", headers=headers_a)
    assert alice_verify_resp.status_code == 404
