"""
Simplified database configuration without Redis dependency
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Database engine (SQLite for simplicity)
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=False
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_redis():
    """Mock Redis client for compatibility"""
    class MockRedis:
        def setex(self, key, time, value):
            pass
        def get(self, key):
            return None
        def ping(self):
            return True
    return MockRedis()

async def init_db():
    """Initialize database tables"""
    try:
        # Import all models to ensure they're registered
        from app.models import Officer, HealthData, LocationData, RiskEvent
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Test database connection
        with SessionLocal() as db:
            db.execute("SELECT 1")
        logger.info("Database connection successful")
        
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

def test_connections():
    """Test database connection"""
    try:
        # Test database
        with SessionLocal() as db:
            db.execute("SELECT 1")
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return False
