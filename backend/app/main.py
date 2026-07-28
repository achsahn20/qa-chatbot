from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app.auth.password import hash_password
from app.config import get_settings
from app.database.base import Base
from app.database.session import SessionLocal, engine
from app.models import User
from app.routes import admin, auth, chat, documents, health


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(auth.router, prefix=settings.api_v1_prefix)
    app.include_router(documents.router, prefix=settings.api_v1_prefix)
    app.include_router(chat.router, prefix=settings.api_v1_prefix)
    app.include_router(admin.router, prefix=settings.api_v1_prefix)

    @app.on_event("startup")
    def on_startup() -> None:
        Base.metadata.create_all(bind=engine)
        with SessionLocal() as db:
            admin_user = db.scalar(select(User).where(User.email == settings.seed_admin_email.lower()))
            if admin_user is None:
                db.add(
                    User(
                        full_name=settings.seed_admin_name,
                        email=settings.seed_admin_email.lower(),
                        password_hash=hash_password(settings.seed_admin_password),
                        role="admin",
                    )
                )
                db.commit()

    return app


app = create_app()
