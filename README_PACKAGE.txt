FakeBuster-AI Package

This archive contains a complete FakeBuster AI project with separate frontend (React) and backend (FastAPI) folders.

Quick start

1. Backend
   - create a virtualenv, activate it
   - pip install -r backend/requirements.txt
   - (optional) edit backend/config.py to add your NYT and NewsAPI keys (already included)
   - run: uvicorn app_main:app --reload --host 0.0.0.0 --port 8000 from backend folder

2. Frontend
   - cd frontend
   - npm install
   - npm start

The frontend will call the backend at http://localhost:8000 by default. Update REACT_APP_BACKEND_URL in frontend/.env if needed.