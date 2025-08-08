from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.dependencies import get_current_active_user
from app.models.user import User
from app.crud.user import user_crud
from pydantic import BaseModel
import secrets
import string
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class BindTelegramRequest(BaseModel):
    telegram_id: int
    telegram_username: str

router = APIRouter(prefix="/telegram", tags=["telegram"])

# Временное хранилище кодов привязки (в продакшене лучше использовать Redis)
binding_codes = {}

def generate_binding_code():
    """Генерирует уникальный код для привязки Telegram"""
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))

def cleanup_expired_codes():
    """Очищает истекшие коды привязки"""
    current_time = datetime.utcnow()
    expired_codes = []
    
    for code, data in binding_codes.items():
        if current_time > data["expires_at"]:
            expired_codes.append(code)
    
    for code in expired_codes:
        del binding_codes[code]
        logger.info(f"Cleaned up expired code: {code}")
    
    if expired_codes:
        logger.info(f"Cleaned up {len(expired_codes)} expired codes")

@router.post("/generate-code")
def generate_binding_code_endpoint(
    current_user: User = Depends(get_current_active_user)
):
    """Генерирует код для привязки Telegram аккаунта"""
    # Очищаем истекшие коды
    cleanup_expired_codes()
    
    # Генерируем уникальный код
    code = generate_binding_code()
    
    # Сохраняем код с временем жизни (10 минут)
    binding_codes[code] = {
        "user_id": current_user.id,
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(minutes=10)
    }
    
    logger.info(f"Generated binding code {code} for user {current_user.id}")
    logger.info(f"Current binding codes: {list(binding_codes.keys())}")
    
    return {
        "code": code,
        "expires_at": binding_codes[code]["expires_at"].isoformat(),
        "message": "Код действителен в течение 10 минут"
    }

@router.post("/unlink")
def unlink_telegram(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Отвязывает Telegram аккаунт от профиля пользователя"""
    if not current_user.telegram_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Telegram аккаунт не привязан"
        )
    
    # Обновляем пользователя, убирая Telegram данные
    update_data = {
        "telegram_id": None,
        "telegram_username": None
    }
    
    updated_user = user_crud.update_admin(db, current_user.id, update_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при отвязке аккаунта"
        )
    
    return {
        "message": "Telegram аккаунт успешно отвязан",
        "user": {
            "id": updated_user.id,
            "username": updated_user.username,
            "telegram_id": updated_user.telegram_id,
            "telegram_username": updated_user.telegram_username
        }
    }

@router.get("/status")
def get_telegram_status(
    current_user: User = Depends(get_current_active_user)
):
    """Получает статус привязки Telegram аккаунта"""
    return {
        "is_linked": bool(current_user.telegram_id and current_user.telegram_username),
        "telegram_id": current_user.telegram_id,
        "telegram_username": current_user.telegram_username
    }

@router.post("/bind/{code}")
def bind_telegram_account(
    code: str,
    request: BindTelegramRequest,
    db: Session = Depends(get_db)
):
    """Привязывает Telegram аккаунт к профилю пользователя по коду"""
    logger.info(f"Received bind request for code: {code}")
    logger.info(f"Request data: {request}")
    
    # Очищаем истекшие коды
    cleanup_expired_codes()
    
    logger.info(f"Attempting to bind code {code} for telegram_id {request.telegram_id}")
    logger.info(f"Available codes: {list(binding_codes.keys())}")
    
    # Проверяем, существует ли код и не истек ли он
    if code not in binding_codes:
        logger.warning(f"Code {code} not found in binding_codes")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недействительный код привязки"
        )
    
    binding_data = binding_codes[code]
    if datetime.utcnow() > binding_data["expires_at"]:
        # Удаляем истекший код
        del binding_codes[code]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Код привязки истек"
        )
    
    user_id = binding_data["user_id"]
    
    # Получаем пользователя
    user = user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    # Проверяем, не привязан ли уже этот Telegram аккаунт к другому пользователю
    existing_user = db.query(User).filter(
        User.telegram_id == request.telegram_id,
        User.id != user_id
    ).first()
    
    if existing_user:
        logger.info(f"Found existing user with telegram_id {request.telegram_id}: user_id {existing_user.id}")
        
        # Если это Telegram-пользователь (без email), то удаляем его и привязываем к веб-пользователю
        if not existing_user.email:
            logger.info(f"Removing Telegram-only user {existing_user.id} to bind to web user {user_id}")
            db.delete(existing_user)
            db.commit()
        else:
            # Если это веб-пользователь с email, то нельзя привязать
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Этот Telegram аккаунт уже привязан к другому пользователю"
            )
    
    # Получаем данные пользователя из Telegram
    telegram_user = db.query(User).filter(User.telegram_id == request.telegram_id).first()
    
    # Обновляем пользователя только Telegram-данными
    update_data = {
        "telegram_id": request.telegram_id,
        "telegram_username": request.telegram_username,
        "is_registered": True  # Устанавливаем флаг регистрации для веб-пользователей
    }
    
    # Не копируем имя пользователя из Telegram, оставляем оригинальное
    
    # Если есть данные из Telegram, добавляем их
    if telegram_user:
        if telegram_user.first_name:
            update_data["first_name"] = telegram_user.first_name
        if telegram_user.last_name:
            update_data["last_name"] = telegram_user.last_name
    
    updated_user = user_crud.update_admin(db, user_id, update_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при привязке аккаунта"
        )
    
    # Удаляем использованный код только после успешной привязки
    del binding_codes[code]
    logger.info(f"Successfully bound code {code} for user {user_id}")
    
    return {
        "message": "Telegram аккаунт успешно привязан",
        "user": {
            "id": updated_user.id,
            "username": updated_user.username,
            "telegram_id": updated_user.telegram_id,
            "telegram_username": updated_user.telegram_username
        }
    }

@router.post("/bind-by-id")
def bind_telegram_by_id(
    telegram_id: int,
    telegram_username: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Привязывает Telegram аккаунт к профилю пользователя по ID"""
    # Проверяем, не привязан ли уже этот Telegram аккаунт к другому пользователю
    existing_user = db.query(User).filter(
        User.telegram_id == telegram_id,
        User.id != current_user.id
    ).first()
    
    if existing_user:
        logger.info(f"Found existing user with telegram_id {telegram_id}: user_id {existing_user.id}")
        
        # Если это Telegram-пользователь (без email), то удаляем его и привязываем к веб-пользователю
        if not existing_user.email:
            logger.info(f"Removing Telegram-only user {existing_user.id} to bind to web user {current_user.id}")
            db.delete(existing_user)
            db.commit()
        else:
            # Если это веб-пользователь с email, то нельзя привязать
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Этот Telegram аккаунт уже привязан к другому пользователю"
            )
    
    # Получаем данные пользователя из Telegram
    telegram_user = db.query(User).filter(User.telegram_id == telegram_id).first()
    
    # Обновляем пользователя только Telegram-данными
    update_data = {
        "telegram_id": telegram_id,
        "telegram_username": telegram_username,
        "is_registered": True  # Устанавливаем флаг регистрации для веб-пользователей
    }
    
    # Не копируем имя пользователя из Telegram, оставляем оригинальное
    
    # Если есть данные из Telegram, добавляем их
    if telegram_user:
        if telegram_user.first_name:
            update_data["first_name"] = telegram_user.first_name
        if telegram_user.last_name:
            update_data["last_name"] = telegram_user.last_name
    
    updated_user = user_crud.update_admin(db, current_user.id, update_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при привязке аккаунта"
        )
    
    return {
        "message": "Telegram аккаунт успешно привязан",
        "user": {
            "id": updated_user.id,
            "username": updated_user.username,
            "telegram_id": updated_user.telegram_id,
            "telegram_username": updated_user.telegram_username
        }
    } 