import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.v1 import api_router
from app.db.session import init_db
from app.core.config import settings
from app.services.settings_service import SettingsService
from app.db.session import AsyncSessionLocal
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up VerifPlatform backend...")
    await init_db()
    async with AsyncSessionLocal() as db:
        await SettingsService.seed_defaults(db)
    logger.info("Database initialized")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded files
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Routes
app.include_router(api_router)


@app.get("/health")
async def health():
    return {"status": "ok", "version": settings.APP_VERSION}
