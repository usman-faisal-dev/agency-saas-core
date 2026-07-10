# Agency Reporting SaaS

AI-powered client reporting platform for agencies. Connect GA4 and Google Ads, generate branded PDF reports grounded in real data, and chat with your metrics in plain English.

> **MVP scope:** SPEC.md — Phase 0 foundation is complete. Follow PLAN.md phases.

---

## Tech Stack

| Layer | Choice |
|---|---|
| Frontend | Next.js 14 + TypeScript (Vercel) |
| Backend  | FastAPI + Python 3.11 (Render) |
| Database | Neon Postgres + SQLAlchemy/Alembic |
| Queue    | Celery + Redis (Render) |
| Auth     | Clerk |
| LLM      | Groq (vendor-agnostic interface) |
| Email    | Resend |
| PDF      | WeasyPrint / Playwright |

---

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 20+
- A running Postgres instance (local or Neon)
- A running Redis instance (local or Upstash)
- Clerk account (free tier works)

---

### Backend

```bash
cd backend

# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your Neon DATABASE_URL, Clerk keys, ENCRYPTION_KEY, etc.

# 4. Generate a Fernet encryption key (run once)
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Paste the output as ENCRYPTION_KEY in .env

# 5. Run database migrations
alembic upgrade head

# 6. Start the FastAPI dev server
uvicorn app.main:app --reload --port 8000
# API docs available at http://localhost:8000/docs
```

**Start Celery worker** (separate terminal):
```bash
cd backend
source .venv/bin/activate
celery -A app.core.celery_app worker --loglevel=info
```

**Run tests:**
```bash
cd backend
pytest --tb=short -q
```

---

### Frontend

```bash
cd frontend

# 1. Install dependencies
npm install

# 2. Configure environment
cp .env.local.example .env.local
# Edit .env.local with your Clerk publishable key and API URL

# 3. Start dev server
npm run dev
# Opens at http://localhost:3000

# Type check:
npm run type-check
```

---

## Deployment

| Service | Platform | Notes |
|---|---|---|
| Frontend | Vercel | Connect the `frontend/` directory; set env vars in Vercel dashboard |
| Backend API | Render (Web Service) | Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Celery Worker | Render (Background Worker) | Start command: `celery -A app.core.celery_app worker --loglevel=info` |
| Database | Neon | Use the pooled connection string for the API; direct string for Alembic |
| Redis | Render Redis | Copy the Redis URL to `REDIS_URL` in both API and Worker env vars |

---

## Project Structure

See [docs/STRUCTURE.md](docs/STRUCTURE.md) for the full annotated directory tree.

## Implementation Plan

See [docs/PLAN.md](docs/PLAN.md) for the 6-phase 30-day roadmap.

## Specification

See [docs/SPEC.md](docs/SPEC.md) for locked MVP scope decisions and data model.
