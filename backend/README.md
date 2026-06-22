# Voicera Backend

AI-powered customer support platform with voice and chat.

## Tech Stack
- FastAPI (Python 3.11)
- Supabase (PostgreSQL + Auth + Storage + Realtime)
- SQLAlchemy async + Alembic
- Celery + Redis (Upstash)
- Pydantic v2
- SlowAPI

## Setup
1. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in the values.
4. Run the server locally:
   ```bash
   uvicorn main:app --reload
   ```
