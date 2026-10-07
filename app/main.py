from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.certificates import router as certificates_router
from app.api.jobs import router as jobs_router
from app.core.config import get_settings
from app.db.init_db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    description="Bulk certificate generation service with job tracking and resilient per-recipient processing.",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(jobs_router)
app.include_router(certificates_router)


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}
