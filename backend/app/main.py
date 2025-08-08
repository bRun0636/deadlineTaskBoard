from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.config import settings
from app.database import engine, Base
from app.api import auth, users, boards, tasks, columns, admin, orders, proposals, messages, telegram
# Импортируем все модели для их регистрации
from app.models import User, Board, Task, Order, Proposal, Message
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем таблицы в базе данных (после импорта всех моделей)
# Base.metadata.create_all(bind=engine)  # Отключаем, используем только миграции

# Создаем экземпляр FastAPI
app = FastAPI(
    title="Deadline Task Board API",
    description="API для управления задачами с дедлайнами и системой заказов",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Обработчик ошибок валидации
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": [
                {
                    "loc": error["loc"],
                    "msg": error["msg"],
                    "type": error["type"]
                }
                for error in exc.errors()
            ]
        }
    )

# Обработчик ValueError
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    logger.error(f"ValueError: {str(exc)}")
    return JSONResponse(
        status_code=400,
        content={
            "detail": str(exc)
        }
    )

# Настройка CORS с улучшенной безопасностью
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.allow_credentials,
    allow_methods=settings.allowed_methods,
    allow_headers=settings.allowed_headers,
    max_age=settings.max_age,
    expose_headers=["Content-Length", "Content-Range"]
)

# Middleware для правильной обработки кодировки
@app.middleware("http")
async def add_charset_middleware(request: Request, call_next):
    response = await call_next(request)
    if "application/json" in response.headers.get("content-type", ""):
        response.headers["content-type"] = "application/json; charset=utf-8"
    return response

# Подключаем роуты
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(boards.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")
app.include_router(columns.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(orders.router, prefix="/api/v1")
app.include_router(proposals.router, prefix="/api/v1")
app.include_router(messages.router, prefix="/api/v1")
app.include_router(telegram.router, prefix="/api/v1")

@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "Deadline Task Board API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """Проверка здоровья API"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    ) 