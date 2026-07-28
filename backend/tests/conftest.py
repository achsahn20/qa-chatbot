from __future__ import annotations

import os
from pathlib import Path
import sys
import tempfile
import uuid

import fitz
import pytest
from fastapi.testclient import TestClient


TEST_ROOT = Path(tempfile.mkdtemp(prefix="docqa-tests-"))
BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

os.environ["DATABASE_URL"] = f"sqlite:///{(TEST_ROOT / 'test.db').as_posix()}"
os.environ["UPLOADS_DIR"] = str(TEST_ROOT / "uploads")
os.environ["CHROMA_PERSIST_DIRECTORY"] = str(TEST_ROOT / "chroma")
os.environ["SECRET_KEY"] = "test-secret"
os.environ["SEED_ADMIN_EMAIL"] = "admin@test.local"
os.environ["SEED_ADMIN_PASSWORD"] = "Admin123!"

from app.config import get_settings

get_settings.cache_clear()

from app.database.base import Base
from app.database.session import SessionLocal, engine
from app.main import create_app
from app.models.user import User


@pytest.fixture(scope="session")
def app():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    return create_app()


@pytest.fixture()
def client(app):
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def auth_headers(client):
    email = f"user-{uuid.uuid4().hex[:8]}@example.com"
    response = client.post(
        "/api/v1/auth/signup",
        json={"full_name": "Test User", "email": email, "password": "Password123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def sample_pdf_bytes():
    document = fitz.open()
    page = document.new_page()
    page.insert_text(
        (72, 72),
        "Employee Handbook\nAnnual leave is 12 days per year.\nSick leave requires manager approval after 3 consecutive days.",
    )
    payload = document.tobytes()
    document.close()
    return payload
