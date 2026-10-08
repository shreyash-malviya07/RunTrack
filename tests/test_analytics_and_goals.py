from datetime import datetime, date, timedelta
import pytest
from fastapi.testclient import TestClient
from database.connection import Base, engine, SessionLocal
from database.models import User
from backend.main import app

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_analytics_db():
    Base.metadata.create_all(bind=engine)
    yield
    db = SessionLocal()
    try:
        db.query(User).filter(User.username.like("analyticstest_%")).delete(synchronize_session=False)
        db.commit()
    finally:
        db.close()


def create_user(username: str, email: str) -> str:
    res = client.post("/auth/register", json={
        "username": username,
        "email": email,
        "password": "Password123!",
        "full_name": f"Runner {username}"
    })
    assert res.status_code == 201
    return res.json()["access_token"]


def test_analytics_and_goals_pipeline():
    token = create_user("analyticstest_carol", "carol@analytics.com")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Log 3 runs over two different weeks
    # Run 1: 5km in 30 mins (Pace 6.0)
    client.post("/runs", headers=headers, json={
        "date": "2026-09-20T07:30:00Z",
        "distance_km": 5.0,
        "duration_minutes": 30.0,
        "calories": 300,
        "avg_heart_rate": 145,
    })
    # Run 2: 10km in 55 mins (Pace 5.5)
    client.post("/runs", headers=headers, json={
        "date": "2026-09-22T08:00:00Z",
        "distance_km": 10.0,
        "duration_minutes": 55.0,
        "calories": 620,
        "avg_heart_rate": 158,
    })
    # Run 3: 15km in 82.5 mins (Pace 5.5)
    client.post("/runs", headers=headers, json={
        "date": "2026-09-28T09:00:00Z",
        "distance_km": 15.0,
        "duration_minutes": 82.5,
        "calories": 950,
        "avg_heart_rate": 162,
    })

    # 2. Check summary analytics
    summary_resp = client.get("/analytics/summary", headers=headers)
    assert summary_resp.status_code == 200
    summary = summary_resp.json()
    assert summary["total_runs"] == 3
    assert summary["total_distance_km"] == 30.0
    assert summary["longest_run_km"] == 15.0
    assert summary["fastest_pace_min_per_km"] == 5.5

    # 3. Check weekly aggregations
    weekly_resp = client.get("/analytics/weekly", headers=headers)
    assert weekly_resp.status_code == 200
    weekly = weekly_resp.json()
    assert len(weekly) >= 2

    # 4. Check dashboard composite endpoint
    dash_resp = client.get("/analytics/dashboard", headers=headers)
    assert dash_resp.status_code == 200
    dash_data = dash_resp.json()
    assert "summary" in dash_data
    assert "insights" in dash_data
    assert len(dash_data["insights"]) > 0

    # 5. Check reports
    rep_resp = client.get("/reports/weekly?week_start=2026-09-28", headers=headers)
    assert rep_resp.status_code == 200
    rep_data = rep_resp.json()
    assert rep_data["total_distance_km"] == 15.0
    assert rep_data["total_runs"] == 1

    # 6. Create Goals
    goal_payload = {
        "goal_type": "custom_distance",
        "target_value": 50.0,
        "start_date": "2026-09-01",
        "deadline": (date.today() + timedelta(days=30)).isoformat(),
        "is_active": True
    }
    goal_res = client.post("/goals", headers=headers, json=goal_payload)
    assert goal_res.status_code == 201
    goal_data = goal_res.json()
    assert goal_data["current_progress"] == 30.0
    assert goal_data["percentage_completion"] == 60.0
    assert goal_data["is_completed"] is False

    # 7. List Goals
    goals_list_res = client.get("/goals", headers=headers)
    assert goals_list_res.status_code == 200
    assert len(goals_list_res.json()) == 1

    # 8. User isolation check on Goals
    other_token = create_user("analyticstest_dan", "dan@analytics.com")
    other_headers = {"Authorization": f"Bearer {other_token}"}
    other_goals_res = client.get("/goals", headers=other_headers)
    assert other_goals_res.status_code == 200
    assert len(other_goals_res.json()) == 0

    goal_id = goal_data["id"]
    unauthorized_goal_get = client.get(f"/goals/{goal_id}", headers=other_headers)
    assert unauthorized_goal_get.status_code == 404
