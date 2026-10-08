from datetime import datetime, date
from typing import Optional, Dict, Any, List
import requests
import streamlit as st
from backend.config import settings

BASE_URL = settings.API_BASE_URL.rstrip("/")


class APIClient:
    def __init__(self):
        self.base_url = BASE_URL

    def _get_headers(self) -> Dict[str, str]:
        token = st.session_state.get("token")
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        if response.status_code == 401:
            st.session_state["token"] = None
            st.session_state["user"] = None
            st.error("Session expired. Please log in again.")
            st.rerun()

        try:
            data = response.json()
        except Exception:
            data = {"detail": response.text}

        if not response.ok:
            error_msg = data.get("detail", "An unexpected error occurred.")
            raise Exception(error_msg)

        return data

    # --- Authentication ---
    def register(self, email: str, username: str, password: str, full_name: Optional[str] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/auth/register"
        resp = requests.post(url, json={
            "email": email,
            "username": username,
            "password": password,
            "full_name": full_name or "",
        })
        return self._handle_response(resp)

    def login(self, username_or_email: str, password: str) -> Dict[str, Any]:
        url = f"{self.base_url}/auth/login"
        resp = requests.post(url, json={
            "username_or_email": username_or_email,
            "password": password,
        })
        return self._handle_response(resp)

    def get_me(self) -> Dict[str, Any]:
        url = f"{self.base_url}/auth/me"
        resp = requests.get(url, headers=self._get_headers())
        return self._handle_response(resp)

    # --- Runs ---
    def get_runs(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        min_distance: Optional[float] = None,
        max_distance: Optional[float] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/runs"
        params = {"limit": limit}
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()
        if min_distance is not None:
            params["min_distance"] = min_distance
        if max_distance is not None:
            params["max_distance"] = max_distance

        resp = requests.get(url, headers=self._get_headers(), params=params)
        return self._handle_response(resp)

    def get_run(self, run_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/runs/{run_id}"
        resp = requests.get(url, headers=self._get_headers())
        return self._handle_response(resp)

    def create_run(self, run_data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/runs"
        resp = requests.post(url, headers=self._get_headers(), json=run_data)
        return self._handle_response(resp)

    def update_run(self, run_id: int, run_data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/runs/{run_id}"
        resp = requests.put(url, headers=self._get_headers(), json=run_data)
        return self._handle_response(resp)

    def delete_run(self, run_id: int) -> bool:
        url = f"{self.base_url}/runs/{run_id}"
        resp = requests.delete(url, headers=self._get_headers())
        if resp.status_code == 204:
            return True
        self._handle_response(resp)
        return False

    # --- Analytics ---
    def get_dashboard_data(self) -> Dict[str, Any]:
        url = f"{self.base_url}/analytics/dashboard"
        resp = requests.get(url, headers=self._get_headers())
        return self._handle_response(resp)

    def get_summary(self) -> Dict[str, Any]:
        url = f"{self.base_url}/analytics/summary"
        resp = requests.get(url, headers=self._get_headers())
        return self._handle_response(resp)

    def get_weekly_analytics(self) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/analytics/weekly"
        resp = requests.get(url, headers=self._get_headers())
        return self._handle_response(resp)

    def get_monthly_analytics(self) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/analytics/monthly"
        resp = requests.get(url, headers=self._get_headers())
        return self._handle_response(resp)

    # --- Reports ---
    def get_weekly_report(self, week_start: Optional[date] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/reports/weekly"
        params = {}
        if week_start:
            params["week_start"] = week_start.isoformat()
        resp = requests.get(url, headers=self._get_headers(), params=params)
        return self._handle_response(resp)

    def get_monthly_report(self, year: Optional[int] = None, month: Optional[int] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/reports/monthly"
        params = {}
        if year:
            params["year"] = year
        if month:
            params["month"] = month
        resp = requests.get(url, headers=self._get_headers(), params=params)
        return self._handle_response(resp)

    # --- Goals ---
    def get_goals(self, active_only: bool = False) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/goals"
        resp = requests.get(url, headers=self._get_headers(), params={"active_only": active_only})
        return self._handle_response(resp)

    def create_goal(self, goal_data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/goals"
        resp = requests.post(url, headers=self._get_headers(), json=goal_data)
        return self._handle_response(resp)

    def update_goal(self, goal_id: int, goal_data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/goals/{goal_id}"
        resp = requests.put(url, headers=self._get_headers(), json=goal_data)
        return self._handle_response(resp)

    def delete_goal(self, goal_id: int) -> bool:
        url = f"{self.base_url}/goals/{goal_id}"
        resp = requests.delete(url, headers=self._get_headers())
        if resp.status_code == 204:
            return True
        self._handle_response(resp)
        return False


api = APIClient()
