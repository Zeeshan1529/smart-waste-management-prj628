# PRJ_628 – Smart Waste Management and Circular Economy Enablement Platform

A modular prototype for CSE7102 Mini Project.

## Current partial implementation
- FastAPI backend
- SQLite database
- Waste-bin monitoring APIs
- Citizen waste report API
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

## Run backend
```bash
cd backend
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000/docs

## Run frontend
```bash
cd frontend
npm install
npm run dev
```

The frontend expects the backend at `http://127.0.0.1:8000`.
