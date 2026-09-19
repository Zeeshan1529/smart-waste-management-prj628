# PRJ_628 – Smart Waste Management and Circular Economy Enablement Platform

A modular prototype for CSE7102 Mini Project.

## Current partial implementation
- FastAPI backend
- MySQL database with SQLAlchemy ORM
- Waste-bin monitoring APIs
- Citizen waste-report API
- Collection-priority engine (rule-based baseline)
- React dashboard scaffold
- ML workspace reserved for waste-generation prediction
- Sample data and API documentation

## Planned next stages
1. Collect/clean historical waste-generation data
2. Train a machine-learning model for collection-demand prediction
3. Add deep-learning waste image classification
4. Add route optimization
5. Add recycler/recovery matching
6. Add role-based authentication and security controls
7. Integrate dashboards and measurable impact analytics

## Database setup (MySQL)

Create the database once in MySQL:

```sql
CREATE DATABASE prj628;
```

Copy the environment template:

```bash
cd backend
cp .env.example .env
```

Edit `backend/.env` and set your MySQL password.

> `backend/.env` is ignored by Git and must not be committed to GitHub.

## Run backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 seed.py
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs

Health check: http://127.0.0.1:8000/health

## Run frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend expects the backend at `http://127.0.0.1:8000`.
