from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql://dbuser:your_secure_password_here@localhost:5432/deadline_task_board")
    test_database_url: str = os.getenv("TEST_DATABASE_URL", "postgresql://dbuser:your_secure_password_here@localhost:5432/test_deadline_task_board")
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "your_very_long_random_secret_key_here_change_in_production")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Server
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # CORS
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost",
        "http://127.0.0.1"
    ]
    
    class Config:
        env_file = ".env"

settings = Settings() 