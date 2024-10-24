import logging
import traceback
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi_async_sqlalchemy import SQLAlchemyMiddleware
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.pool import NullPool
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings, ModeEnum
from app.api.api import api_router
from app.core.limiter import limiter

app = FastAPI()

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    SQLAlchemyMiddleware,
    db_url=str(settings.ASYNC_DATABASE_URI),
    engine_args={
        "echo": False,
        "poolclass": NullPool
        # if settings.MODE == ModeEnum.testing
        # else AsyncAdaptedQueuePool
        # "pool_pre_ping": True,
        # "pool_size": settings.POOL_SIZE,
        # "max_overflow": 64,
    },
)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["Content-Type", "Authorization"],
    )


@app.middleware('http')
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["X-Frame-Options"] = "DENY"
    csp = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "img-src 'self' https://fastapi.tiangolo.com data:; "
        "font-src 'self' https://cdn.jsdelivr.net; "
        "connect-src 'self'; "
        "frame-src 'self'; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "form-action 'self'; "
        "frame-ancestors 'none'; "
        "worker-src 'self' blob:; "
    )

    if settings.MODE in [ModeEnum.development, ModeEnum.testing]:
        response.headers["Content-Security-Policy"] = csp
    else:
        # In production, you might want to use a more restrictive policy
        response.headers["Content-Security-Policy"] = "default-src 'self'"

    # Allow CORS for localhost
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:8000"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"

    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    error_message = str(exc)
    error_type = type(exc).__name__
    error_traceback = ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    error_timestamp = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    error_derails = {
        "error_message": error_message,
        "error_type": error_type,
        "error_traceback": error_traceback,
        "error_timestamp": error_timestamp,
        "method": request.method,
        "endpoint": request.url.path,
    }
    logging.error(f"An error occurred: {error_derails}")
    return JSONResponse(
        content={
            "error": "Internal Server Error",
        },
        status_code=500
    )


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(api_router)
