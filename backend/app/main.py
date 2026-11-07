import json
import logging
import sqlite3
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.actions.routes import router as actions_router
from app.agent.worker import start_worker, stop_worker
from app.analytics.routes import router as analytics_router
from app.analytics.service import record_request
from app.auth.routes import router as auth_router
from app.cases.routes import router as cases_router
from app.documents.routes import router as documents_router
from app.evidence.routes import router as evidence_router
from app.knowledge.routes import router as knowledge_router
from app.notifications.routes import router as notifications_router
from app.planning.routes import router as planning_router
from app.shared.config import ROOT, worker_enabled
from app.shared.contracts import Bootstrap, ErrorResponse, Health
from app.shared.db import SCHEMA_VERSION, connect, initialize

logger = logging.getLogger("onboardiq.api")
logging.basicConfig(level=logging.INFO, format="%(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize()
    if worker_enabled():
        start_worker()
    yield
    if worker_enabled():
        stop_worker()


app = FastAPI(title="OnboardIQ", version="0.2.0", lifespan=lifespan)


@app.middleware("http")
async def observe(request: Request, call_next):
    """Structured request log. Holds no body, query string, token or document content."""
    request_id = uuid.uuid4().hex[:12]
    started = time.monotonic()
    status = 500
    try:
        response = await call_next(request)
        status = response.status_code
        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        elapsed = (time.monotonic() - started) * 1000
        if request.url.path.startswith("/api"):
            record_request(elapsed, status)
            logger.info(
                json.dumps(
                    {
                        "event": "api_request",
                        "request_id": request_id,
                        "method": request.method,
                        "path": request.url.path,
                        "status": status,
                        "ms": round(elapsed, 1),
                    }
                )
            )


@app.exception_handler(StarletteHTTPException)
async def http_error(request: Request, exc: StarletteHTTPException):
    detail = (
        exc.detail
        if isinstance(exc.detail, dict)
        else {
            "code": f"HTTP_{exc.status_code}",
            "message": str(exc.detail),
            "details": [],
        }
    )
    return JSONResponse(status_code=exc.status_code, content={"error": detail}, headers=exc.headers)


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    # Do not echo invalid input: it could be a password or sensitive document.
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request does not match the contract.",
                "details": [
                    {"field": ".".join(map(str, item["loc"])), "message": item["msg"]}
                    for item in exc.errors()
                ],
            }
        },
    )


@app.exception_handler(Exception)
async def unexpected_error(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s", request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "Something went wrong. Nothing was reported as done.",
                "details": [],
            }
        },
    )


@app.get("/health", response_model=Health, include_in_schema=False)
@app.get(
    "/api/health",
    response_model=Health,
    tags=["foundation"],
    responses={503: {"model": ErrorResponse}},
    summary="Read database-backed readiness",
)
def health():
    try:
        with connect() as connection:
            row = connection.execute("SELECT schema_version FROM app_info WHERE id=1").fetchone()
            if row is None or row["schema_version"] != SCHEMA_VERSION:
                raise sqlite3.DatabaseError("Unsupported schema")
        return Health()
    except sqlite3.Error as exc:
        raise HTTPException(
            503,
            detail={
                "code": "DATABASE_UNAVAILABLE",
                "message": "Local database is unavailable.",
                "details": [],
            },
        ) from exc


@app.get(
    "/api/bootstrap",
    response_model=Bootstrap,
    tags=["foundation"],
    responses={503: {"model": ErrorResponse}},
    summary="Read the product name stored in SQLite",
)
def bootstrap():
    health()
    with connect() as connection:
        row = connection.execute("SELECT project_name FROM app_info WHERE id=1").fetchone()
    return Bootstrap(
        project_name=row["project_name"],
        message="Frontend, backend and SQLite are connected. All data is synthetic.",
    )


errors = {code: {"model": ErrorResponse} for code in (401, 403, 404, 409, 422)}
# Python 3.12 and 3.13 have different default reason phrases for HTTP 422.
errors[422]["description"] = "Unprocessable Content"
for router in (
    auth_router,
    planning_router,
    evidence_router,
    documents_router,
    cases_router,
    actions_router,
    knowledge_router,
    notifications_router,
    analytics_router,
):
    app.include_router(router, prefix="/api", responses=errors)

# Built assets are served by the same trusted origin. Never mount the repository or .env.
dist = ROOT / "frontend" / "dist"
if dist.is_dir():
    if (dist / "assets").is_dir():
        app.mount("/assets", StaticFiles(directory=dist / "assets"), name="assets")

    @app.get("/", include_in_schema=False)
    def index():
        return FileResponse(Path(dist / "index.html"))
