"""FastAPI 애플리케이션 생성과 공통 미들웨어를 구성한다."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.content_types import router as content_types_router
from app.api.comments import router as comments_router
from app.api.places import router as places_router
from app.api.posts import router as posts_router
from app.api.endpoints import chat
from app.core.config import get_settings
from app.core.database import init_db


# 필수 환경변수가 빠졌다면 서버 시작 단계에서 즉시 알 수 있도록 먼저 검증한다.
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 시작 시 ORM 모델에 필요한 테이블을 준비한다."""
    init_db()
    yield


app = FastAPI(
    title="Team Project API",
    description="Team Project Backend API",
    version="1.0.0",
    lifespan=lifespan,
)

# 허용할 프론트엔드 출처는 소스가 아닌 환경변수에서 관리한다.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(content_types_router)
app.include_router(places_router)
app.include_router(posts_router)
app.include_router(comments_router)
app.include_router(chat.router, prefix="/api", tags=["chat"])

@app.get("/")
def read_root():
    """API 기본 안내 메시지를 반환한다."""
    return {"message": "Team Project Backend API"}

@app.get("/health")
def health_check():
    """서버가 요청을 처리할 수 있는지 확인한다."""
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
