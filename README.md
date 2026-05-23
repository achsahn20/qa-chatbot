# Document Q&A Chatbot using RAG, FastAPI, PostgreSQL, and Vector Database

Production-style portfolio project for uploading PDFs, indexing them into a vector store, and answering natural-language questions with grounded citations.

## Stack

- Frontend: React, TypeScript, Tailwind CSS, React Router, Axios
- Backend: FastAPI, SQLAlchemy, JWT auth, PyMuPDF
- Data: PostgreSQL-compatible SQLAlchemy models, ChromaDB vector store
- AI: pluggable embedding and answer-generation providers with local fallbacks

## Key Features

- User signup, login, and protected workspace routes
- PDF upload and background processing
- Text extraction, chunking, embeddings, and vector indexing
- Citation-backed Q&A with page number and source quotes
- Chat sessions and message history
- Admin dashboard for top-level usage insight

## Local Run

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
copy .env.example .env
npm install
npm run dev
```

The frontend expects the backend at `http://localhost:8000/api/v1`.

## Demo Admin

- Email: `admin@example.com`
- Password: `Admin123!`

## Tests

```bash
cd backend
pytest
```

## Docker

```bash
docker compose up --build
```
# Implementation Audit

This project was checked against the original implementation plan for a production-style Document Q&A chatbot.

## Verified Working

- React frontend codebase with routing, auth context, dashboard, upload, documents, chat, history, admin, and settings screens
- FastAPI backend with auth, document upload/list/delete/reprocess, chat session APIs, admin APIs, and health check
- PDF parsing with PyMuPDF
- Chunking, metadata capture, retrieval, citation formatting, and chat history persistence
- JWT authentication and bcrypt password hashing
- PostgreSQL-ready SQLAlchemy models and Docker Compose PostgreSQL service
- Alembic migration scaffolding and an initial schema migration
- Frontend production build
- Backend automated tests
- End-to-end HTTP verification for signup, upload, processing, chat answer generation, citations, and admin dashboard

## Intentional Local Defaults

- Local development defaults to SQLite for convenience. PostgreSQL is supported via `DATABASE_URL` and is wired in `docker-compose.yml`.
- The repository uses a lightweight persistent vector-store adapter by default for easy local execution without extra infrastructure.
- OpenAI-backed embeddings and answer generation are supported by configuration, but the app falls back to a local extractive mode when no API key is provided.

## Current Tradeoffs Versus The Original Plan

- The default local vector implementation is not ChromaDB or FAISS, though the RAG layer is structured so it can be swapped to Chroma/pgvector/Qdrant later.
- The default no-key answer generator is a deterministic fallback rather than a hosted LLM. This keeps the project runnable without external credentials.
- The app currently creates tables on startup for convenience in addition to including Alembic migrations. For stricter production behavior, startup table creation can be removed once migrations are the only schema path.

## Verification Summary

- Backend tests: passed
- Frontend build: passed
- Runtime health check: passed
- Upload and RAG chat flow: passed
- Admin dashboard API: passed
- Alembic migration smoke test: passed
