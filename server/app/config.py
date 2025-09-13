"""
Configuration settings for the First Responder Risk Monitoring API
"""

from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/first_responder_risk"
    REDIS_URL: str = "redis://localhost:6379"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "First Responder Risk Monitoring"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080"
    ]
    
    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30
    
    # Risk Scoring
    RISK_UPDATE_INTERVAL: int = 5  # seconds
    HIGH_RISK_THRESHOLD: float = 0.7
    MEDIUM_RISK_THRESHOLD: float = 0.4
    
    # Location
    DEFAULT_LATITUDE: float = 40.7128  # New York City
    DEFAULT_LONGITUDE: float = -74.0060
    LOCATION_ACCURACY_THRESHOLD: float = 100.0  # meters
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()
