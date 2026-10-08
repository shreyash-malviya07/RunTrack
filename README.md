# 🏃 RunTrack — Professional Running Analytics Platform

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.39+-FF4B4B.svg)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-5.24+-3F4F75.svg)](https://plotly.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

RunTrack is an athletic analytics and training intelligence platform built as a 3-person engineering project. It enables runners to log activities, track performance trajectories, monitor goals, generate period-over-period comparison reports, and receive automated rule-based coaching insights.

---

## 🏗️ Architecture & Tech Stack

```text
               +-------------------------------------------+
               |        Streamlit + Plotly Frontend        |
               |        (Port 8501 - Multi-Page App)       |
               +---------------------+---------------------+
                                     |
                                     |  HTTP REST / Bearer JWT
                                     v
               +-------------------------------------------+
               |              FastAPI Backend              |
               |             (Port 8000 - ASGI)            |
               +----------+---------------------+----------+
                          |                     |
                          v                     v
               +--------------------+ +--------------------+
               |   SQLAlchemy ORM   | |   Pandas Analytics |
               |     (SQLite DB)    | |     Engine Core    |
               +--------------------+ +--------------------+
```

* **Frontend**: Streamlit, Plotly (Interactive charts, dark/light theme)
* **Backend**: FastAPI, Pydantic v2, Uvicorn
* **Database**: SQLite, SQLAlchemy ORM (Strict user isolation & foreign key cascades)
* **Analytics**: Pandas, NumPy (Vectorized metrics, rolling paces, rule-based insights)
* **Security**: Bcrypt password hashing, signed JWT access tokens (PyJWT)

---

## 📁 Project Directory Structure

```text
RUNTRACK/
├── backend/                  # FastAPI Application
│   ├── main.py               # Application factory & router registration
│   ├── config.py             # Environment configuration (Pydantic Settings)
│   ├── dependencies.py       # JWT Bearer token & DB session dependencies
│   ├── routes/               # Modular REST API endpoints
│   │   ├── auth.py           # /auth (register, login, me)
│   │   ├── runs.py           # /runs CRUD
│   │   ├── goals.py          # /goals CRUD & progress
│   │   ├── analytics.py      # /analytics (summary, weekly, monthly, insights)
│   │   └── reports.py        # /reports (weekly, monthly comparisons)
│   ├── schemas/              # Pydantic v2 request/response schemas
│   │   ├── user.py
│   │   ├── run.py
│   │   ├── goal.py
│   │   ├── analytics.py
│   │   └── report.py
│   └── services/             # Business logic & user-isolated database queries
│       ├── auth_service.py
│       ├── run_service.py
│       └── goal_service.py
│
├── database/                 # Data Persistence Layer
│   ├── connection.py         # SQLAlchemy engine, session maker, get_db
│   ├── models.py             # ORM models (User, Run, Goal, WeeklyReport)
│   └── seed.py               # Demo runner activity & goals generator
│
├── analytics/                # Pure Analytics Engine
│   ├── metrics.py            # Aggregations, paces, consistency, streaks
│   ├── insights.py           # Rule-based coaching engine (10% rule, PRs)
│   └── reports.py            # Period-over-period comparison algorithms
│
├── frontend/                 # Streamlit UI Support
│   ├── api_client.py         # Type-safe API client forwarding JWT tokens
│   ├── components.py         # Auth guard, sidebar, metric & insight cards
│   └── charts.py             # Plotly interactive chart builders
│
├── pages/                    # Multi-Page Navigation
│   ├── 1_🏃_Dashboard.py    # High-level KPIs, weekly volume, pace trend, insights
│   ├── 2_📋_My_Runs.py      # Search, filter, edit, and delete activities
│   ├── 3_➕_Add_Run.py       # Activity logging with instant pace calculator
│   ├── 4_📊_Analytics.py    # Deep-dive athletic charts & consistency scores
│   ├── 5_📑_Reports.py      # Weekly & monthly period reports
│   ├── 6_🎯_Goals.py        # Target progress bars, countdowns, and creation
│   └── 7_👤_Profile.py      # Runner stats, account metadata, and sign out
│
├── data/                     # SQLite database files (.gitignored)
├── tests/                    # Automated Pytest suite
│   ├── test_auth.py
│   ├── test_runs.py
│   └── test_analytics_and_goals.py
│
├── app.py                    # Streamlit app entrypoint & auth controller
├── run_backend.sh            # One-click FastAPI backend launcher
├── run_frontend.sh           # One-click Streamlit frontend launcher
├── requirements.txt          # Pinned dependencies
├── .env.example              # Environment variables template
└── README.md
```

---

## 👥 3-Developer Team Division of Responsibilities

To avoid merge conflicts, each developer owns a distinct layer with strict contract boundaries:

| Developer | Domain & Modules | Key Files Owned |
|---|---|---|
| **Developer 1** | Backend Core, Auth & Database | `database/`, `backend/routes/auth.py`, `backend/routes/runs.py`, `backend/services/` |
| **Developer 2** | Analytics, Reports & Goals Engine | `analytics/`, `backend/routes/analytics.py`, `backend/routes/reports.py`, `backend/routes/goals.py` |
| **Developer 3** | Frontend, Streamlit & Plotly Charts | `app.py`, `pages/`, `frontend/api_client.py`, `frontend/charts.py`, `frontend/components.py` |

---

## 🚀 Quick Start Guide

### 1. Prerequisites & Environment Setup
Clone the repository and set up a Python 3.13 virtual environment:

```bash
cd ~/RUNTRACK
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 2. Seed Demo Data (Optional but Recommended)
Populate 17 realistic runs spread across 6 weeks and 2 active goals:

```bash
PYTHONPATH=. python database/seed.py
```

* **Demo Username**: `elite_runner`
* **Demo Password**: `RunTrack2026!`

### 3. Launch the Application

In **Terminal 1** (Backend):
```bash
./run_backend.sh
# Running at http://127.0.0.1:8000
# OpenAPI Docs at http://127.0.0.1:8000/docs
```

In **Terminal 2** (Frontend):
```bash
./run_frontend.sh
# Running at http://127.0.0.1:8501
```

Open your browser to [http://localhost:8501](http://localhost:8501) and sign in!

---

## 🧪 Running Automated Tests

Run the complete test suite:

```bash
PYTHONPATH=. .venv/bin/pytest -v
```

All tests verify user isolation, JWT authentication, calculations, and CRUD flows.
