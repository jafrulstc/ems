"""
FastAPI application entry point.

Responsibilities:
  - Create the FastAPI app instance with metadata
  - Register middleware (CORS, TenantMiddleware)
  - Mount all feature routers under /api/v1
  - Register global exception handlers
  - Expose /healthz liveness probe
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.config import get_settings
from app.database import engine
from app.middleware.tenant import TenantMiddleware

settings = get_settings()
logger = logging.getLogger("uvicorn.error")


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Verify DB connectivity on startup; dispose engine on shutdown."""
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    logger.info("✅ Database connection verified.")
    yield
    await engine.dispose()
    logger.info("🛑 Database engine disposed.")


# ── App instance ──────────────────────────────────────────────────────────────

app = FastAPI(
    title="Multi-Tenant EMS API",
    description="Education Management System — multi-tenant, schema-per-feature.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# ── Middleware ────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TenantMiddleware must be added AFTER CORSMiddleware
app.add_middleware(TenantMiddleware)


# ── Global exception handlers ─────────────────────────────────────────────────

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception on %s %s", request.method, request.url)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"success": False, "message": "An unexpected error occurred.", "data": None},
    )


# ── Health probe ──────────────────────────────────────────────────────────────

@app.get("/healthz", tags=["Health"], include_in_schema=False)
async def health_check():
    return {"status": "ok", "env": settings.APP_ENV}


# ── Feature routers ───────────────────────────────────────────────────────────
from app.features.core.router import router as core_router
app.include_router(core_router, prefix="/api/v1/core", tags=["Core"])

# Phase 3+: from app.features.auth.router import router as auth_router
#            app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
# Phase 4+: from app.features.academic.router import router as academic_router
#            app.include_router(academic_router, prefix="/api/v1/academic", tags=["Academic"])
# Phase 5+: from app.features.exam.router import router as exam_router
#            app.include_router(exam_router, prefix="/api/v1/exam", tags=["Exam"])
