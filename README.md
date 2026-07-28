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
