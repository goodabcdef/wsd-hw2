import time
from datetime import datetime
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
import logging

# Rate Limiting (과제 필수 1-7)
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.db.session import engine, Base
# 새로 만든 라우터들까지 모두 포함
from app.api.v1.endpoints import users, auth, books, cart, orders, reviews, favorites, stats

# 로그 포맷: [시간] [레벨] 메시지
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# DB 테이블 생성 함수
def create_tables():
    Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 앱 시작 시 테이블 생성 (실무에선 Alembic을 쓰지만 과제용으로 유지)
    create_tables()
    yield

# Rate Limiter 설정 (하루 1000회, 분당 100회 제한)
limiter = Limiter(key_func=get_remote_address, default_limits=["1000/day", "100/minute"])

app = FastAPI(lifespan=lifespan, title="JCloud Bookstore")

# Rate Limiter 등록
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# [과제 필수 1-7] CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인 허용 (보안상 특정 도메인이 좋으나 과제/테스트용은 * 가능)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# [과제 필수 1-9] 로깅 미들웨어 (요청 처리 시간 및 경로 로깅)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # 민감 정보(Body, Password 등)는 제외하고 핵심 정보만 로그에 남김
        logger.info(
            f"Method={request.method} Path={request.url.path} "
            f"Status={response.status_code} Latency={process_time:.4f}s"
        )
        return response
        
    except Exception as e:
        # 미들웨어 단계에서 터진 예상치 못한 에러 처리
        process_time = time.time() - start_time
        logger.error(
            f"Method={request.method} Path={request.url.path} "
            f"Status=500 Latency={process_time:.4f}s"
        )
        raise e # 에러 핸들러로 넘김

# [과제 필수 1-4 & 4-1] 표준 에러 응답 생성 함수
def create_error_response(status_code: int, code: str, message: str, path: str, details: dict = None):
    return JSONResponse(
        status_code=status_code,
        content={
            "timestamp": datetime.now().isoformat(),
            "path": path,
            "status": status_code,
            "code": code,
            "message": message,
            "details": details
        }
    )

# 일반적인 HTTP 예외 핸들러 (401, 403, 404 등)
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    # 에러 코드 매핑 (최소 10종 이상 정의)
    code_mapping = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",        # [추가] 허용되지 않은 메소드 (GET 대신 POST 등)
        406: "NOT_ACCEPTABLE",            # [추가] 클라이언트가 받을 수 없는 포맷
        408: "REQUEST_TIMEOUT",           # [추가] 요청 시간 초과
        409: "CONFLICT",
        415: "UNSUPPORTED_MEDIA_TYPE",    # [추가] 지원하지 않는 미디어 타입 (Content-Type 에러)
        422: "UNPROCESSABLE_ENTITY",      # [추가] 문법은 맞으나 처리할 수 없는 데이터
        429: "TOO_MANY_REQUESTS",
        500: "INTERNAL_SERVER_ERROR",
        502: "BAD_GATEWAY",               # [추가] 게이트웨이 오류
        503: "SERVICE_UNAVAILABLE"        # [추가] 서버 과부하/점검
    }

    error_code = code_mapping.get(exc.status_code, "HTTP_ERROR")

    return create_error_response(
        status_code=exc.status_code,
        code=error_code,
        message=str(exc.detail),
        path=request.url.path
    )
    
    
# 에러 발생 시 스택트레이스 로그 남기기 (500 에러)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # [중요] exc_info=True 옵션이 스택트레이스를 로그에 출력해줍니다.
    logger.error(f"🔥 500 Internal Server Error: {str(exc)}", exc_info=True)

    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="INTERNAL_SERVER_ERROR",
        message="서버 내부 오류가 발생했습니다. 관리자에게 문의하세요.",
        path=request.url.path
    )

# 유효성 검사 실패 핸들러 (Pydantic Validation Error)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    details = {}
    for error in exc.errors():
        # loc가 ('body', 'email') 처럼 나오는데 이를 'email' 문자열로 변환
        field = ".".join(str(x) for x in error['loc'][1:]) 
        details[field] = error['msg']

    return create_error_response(
        status_code=status.HTTP_400_BAD_REQUEST, # 과제 에러 규격에 맞춤
        code="VALIDATION_FAILED",
        message="입력값이 올바르지 않습니다.",
        path=request.url.path,
        details=details
    )


# API 라우터 등록
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(books.router, prefix="/api/v1/books", tags=["books"])
app.include_router(cart.router, prefix="/api/v1/cart", tags=["cart"])
app.include_router(orders.router, prefix="/api/v1/orders", tags=["orders"])
app.include_router(reviews.router, prefix="/api/v1", tags=["reviews"]) 
app.include_router(favorites.router, prefix="/api/v1", tags=["favorites"])
app.include_router(stats.router, prefix="/api/v1/stats", tags=["stats"])

@app.get("/")
def read_root():
    return {"message": "Hello, JCloud Bookstore!"}

# [과제 필수 1-7] 헬스체크
@app.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=False)