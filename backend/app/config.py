from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv("DATABASE_URL", "")
    test_database_url: str = os.getenv("TEST_DATABASE_URL", "")
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Server
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # API Base URL for internal requests
    api_base_url: str = os.getenv("API_BASE_URL", "http://localhost:8000")
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000"]
    
    @property
    def cors_origins(self) -> List[str]:
        origins_str = os.getenv("ALLOWED_ORIGINS")
        if origins_str:
            try:
                import json
                return json.loads(origins_str)
            except json.JSONDecodeError:
                return origins_str.split(",")
        return self.allowed_origins
    allowed_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
    allowed_headers: List[str] = [
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "Accept",
        "Origin",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers"
    ]
    allow_credentials: bool = True
    max_age: int = 600  # 10 минут кэширования preflight-запросов
    
    class Config:
        env_file = ".env"

settings = Settings() 