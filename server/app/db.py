"""
Database configuration and session management
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID
import redis
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Redis connection
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_redis():
    """Dependency to get Redis client"""
    return redis_client

async def init_db():
    """Initialize database tables"""
    try:
        # Import all models to ensure they're registered
        from app.models import Officer, HealthData, LocationData, RiskEvent
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Test Redis connection
        redis_client.ping()
        logger.info("Redis connection successful")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

def test_connections():
    """Test database and Redis connections"""
    try:
        # Test database
        with SessionLocal() as db:
            db.execute("SELECT 1")
        logger.info("Database connection successful")
        
        # Test Redis
        redis_client.ping()
        logger.info("Redis connection successful")
        
        return True
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return False
