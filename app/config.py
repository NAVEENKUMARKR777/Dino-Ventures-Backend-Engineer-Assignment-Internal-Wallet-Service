"""
Configuration management for the wallet service.
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://wallet_user:wallet_pass@localhost:5432/wallet_db"
    
    # Application
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "info"
    API_VERSION: str = "v1"
    APP_NAME: str = "Dino Ventures Wallet Service"
    
    # Security
    SECRET_KEY: str = "change-this-in-production"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Transaction Limits
    MAX_TRANSACTION_AMOUNT: float = 1000000.0
    MIN_TRANSACTION_AMOUNT: float = 0.01
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
