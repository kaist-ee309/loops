import traceback
import uuid
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from time import time

from fastapi import FastAPI, Request, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api import OPENAPI_TAGS
from app.api import router as api_router
from app.config import settings
from app.core.exceptions import LoopsAPIException
from app.core.logging import logger, setup_logging
from app.database import engine

# Track application start time for uptime calculation
APP_START_TIME = time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 시작 및 종료 시 실행되는 라이프사이클 관리자."""
    # Startup: Configure logging
    setup_logging()
    logger.info("Application starting", version=settings.app_version)

    yield

    # Shutdown: Dispose database engine
    logger.info("Application shutting down")
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    description="""
## Loops API - 영어 단어 학습 애플리케이션 백엔드

FSRS(Free Spaced Repetition Scheduler) 알고리즘 기반의 효율적인 영어 단어 암기 학습을 지원하는 API입니다.

### 주요 기능

- **인증**: Supabase Auth를 통한 안전한 사용자 인증
- **단어 카드**: 영어 단어, 발음, 예문 등을 포함한 학습 카드 관리
- **FSRS 복습**: 과학적 간격 반복 알고리즘으로 최적의 복습 시점 계산
- **덱 관리**: 주제별 단어장 구성 및 선택적 학습
- **학습 통계**: 정확도, 스트릭, CEFR 레벨별 진행 상황 추적

### 인증 방식

Bearer Token 인증을 사용합니다. `/auth/login` 또는 `/auth/register`에서 발급받은 `access_token`을
`Authorization: Bearer {token}` 헤더에 포함하여 요청하세요.
""",
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
    openapi_tags=OPENAPI_TAGS,
)


# Middleware for request ID tracking
@app.middleware("http")
async def add_request_id_middleware(request: Request, call_next):
    """Add unique request ID to each request for tracking."""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    # Add request ID to logger context
    with logger.contextualize(request_id=request_id):
        logger.info(
            "Request started",
            method=request.method,
            path=request.url.path,
            client=request.client.host if request.client else None,
        )

        start_time = time()
        response = await call_next(request)
        duration = time() - start_time

        logger.info(
            "Request completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration * 1000, 2),
        )

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(LoopsAPIException)
async def loops_api_exception_handler(request: Request, exc: LoopsAPIException):
    """Handle custom Loops API exceptions."""
    request_id = getattr(request.state, "request_id", None)

    logger.error(
        "API exception occurred",
        error_type=exc.error_type,
        message=exc.message,
        status_code=exc.status_code,
        path=request.url.path,
        method=request.method,
        details=exc.details,
        request_id=request_id,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_type,
            "message": exc.message,
            **exc.details,
        },
        headers={"X-Request-ID": request_id} if request_id else {},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors."""
    request_id = getattr(request.state, "request_id", None)

    errors = jsonable_encoder(exc.errors())

    logger.warning(
        "Validation error",
        method=request.method,
        path=request.url.path,
        errors=errors,
        request_id=request_id,
    )

    return JSONResponse(
        status_code=400,
        content={
            "error": "validation_error",
            "message": "Invalid request data",
            "details": errors,
        },
        headers={"X-Request-ID": request_id} if request_id else {},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handle all uncaught exceptions."""
    request_id = getattr(request.state, "request_id", None)

    # Log full traceback
    logger.exception(
        "Unhandled exception",
        exception_type=type(exc).__name__,
        exception_message=str(exc),
        path=request.url.path,
        method=request.method,
        request_id=request_id,
    )

    # Don't expose internal errors in production
    if settings.debug:
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_server_error",
                "message": str(exc),
                "traceback": traceback.format_exc(),
            },
            headers={"X-Request-ID": request_id} if request_id else {},
        )
    else:
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_server_error",
                "message": "An unexpected error occurred. Please try again later.",
            },
            headers={"X-Request-ID": request_id} if request_id else {},
        )


# Include API routes
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get(
    "/",
    summary="API 루트",
    description="API 정보 및 문서 링크를 반환합니다.",
    responses={
        200: {"description": "API 기본 정보 반환 성공"},
    },
)
async def root():
    """
    API 루트 엔드포인트.

    Loops API의 기본 정보와 API 문서 링크를 반환합니다.
    인증 없이 접근 가능합니다.
    """
    return {
        "message": "Welcome to Loops API",
        "version": settings.app_version,
        "docs": "/docs",
    }


@app.get(
    "/health",
    summary="헬스 체크",
    description="API 서버 및 데이터베이스 연결 상태를 확인합니다.",
    responses={
        200: {"description": "서비스 정상 작동 중"},
        503: {"description": "서비스 이상 - 데이터베이스 연결 실패 등"},
    },
)
async def health(response: Response):
    """
    헬스 체크 엔드포인트.

    서버 상태 및 데이터베이스 연결을 확인하고 서비스 상태를 반환합니다.

    **반환 정보:**
    - `status`: 서비스 상태 (healthy/unhealthy)
    - `version`: API 버전
    - `uptime_seconds`: 서버 가동 시간 (초)
    - `timestamp`: 현재 시간 (ISO 8601)
    - `database`: 데이터베이스 연결 상태 (connected/disconnected)

    **주의:** 데이터베이스 연결 실패 시 HTTP 503을 반환합니다.
    """
    uptime_seconds = int(time() - APP_START_TIME)
    timestamp = datetime.now(UTC).isoformat()

    health_status = {
        "status": "healthy",
        "version": settings.app_version,
        "uptime_seconds": uptime_seconds,
        "timestamp": timestamp,
        "database": "unknown",
    }

    # Test database connection
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            health_status["database"] = "connected"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["database"] = "disconnected"
        health_status["error"] = str(e)
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return health_status
