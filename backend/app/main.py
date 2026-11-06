import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.actions.routes import router as actions_router
from app.auth.routes import router as auth_router
from app.cases.routes import router as cases_router
from app.evidence.routes import router as evidence_router
from app.planning.routes import router as planning_router
from app.shared.config import ROOT
from app.shared.contracts import Bootstrap, ErrorResponse, Health
from app.shared.db import connect, initialize


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize()
    yield


app = FastAPI(title="DayOne Proof", version="0.1.0", lifespan=lifespan)


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
            if row is None or row["schema_version"] != 1:
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
    summary="Read hello-world value stored in SQLite",
)
def bootstrap():
    health()
    with connect() as connection:
        row = connection.execute("SELECT project_name FROM app_info WHERE id=1").fetchone()
    return Bootstrap(
        project_name=row["project_name"],
        message="Frontend, backend and SQLite are connected. Business features are stubs.",
    )


errors = {code: {"model": ErrorResponse} for code in (401, 403, 404, 409, 422, 501)}
# Python 3.12 and 3.13 have different default reason phrases for HTTP 422.
errors[422]["description"] = "Unprocessable Content"
for router in (auth_router, planning_router, evidence_router, cases_router, actions_router):
    app.include_router(router, prefix="/api", responses=errors)

# Built assets are served by the same trusted origin. Never mount the repository or .env.
dist = ROOT / "frontend" / "dist"
if dist.is_dir():
    if (dist / "assets").is_dir():
        app.mount("/assets", StaticFiles(directory=dist / "assets"), name="assets")

    @app.get("/", include_in_schema=False)
    def index():
        return FileResponse(Path(dist / "index.html"))
