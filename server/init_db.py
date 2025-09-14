"""
Initialize database with sample data
"""

import asyncio
import uuid
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from app.db_simple import engine, Base
from app.models import Officer, HealthData, LocationData, RiskEvent

# Create all tables
Base.metadata.create_all(bind=engine)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_sample_data():
    """Create sample officers and data"""
    db = SessionLocal()
    
    try:
        # Create sample officers
        officers = [
            Officer(
                id="550e8400-e29b-41d4-a716-446655440000",
                badge_number="PD001",
                name="John Smith",
                department="Police Department",
                phone="+1-555-0101",
                email="john.smith@pd.gov",
                is_active=True,
                is_on_duty=True,
                device_id="device_001",
                app_version="1.0.0",
                current_risk_level="low",
                current_risk_score=0.2
            ),
            Officer(
                id="550e8400-e29b-41d4-a716-446655440001",
                badge_number="FD002",
                name="Sarah Johnson",
                department="Fire Department",
                phone="+1-555-0102",
                email="sarah.johnson@fd.gov",
                is_active=True,
                is_on_duty=True,
                device_id="device_002",
                app_version="1.0.0",
                current_risk_level="medium",
                current_risk_score=0.5
            ),
            Officer(
                id="550e8400-e29b-41d4-a716-446655440002",
                badge_number="EMT003",
                name="Mike Davis",
                department="Emergency Medical",
                phone="+1-555-0103",
                email="mike.davis@emt.gov",
                is_active=True,
                is_on_duty=False,
                device_id="device_003",
                app_version="1.0.0",
                current_risk_level="low",
                current_risk_score=0.1
            )
        ]
        
        for officer in officers:
            db.add(officer)
        
        # Create some sample health data
        health_data = HealthData(
            officer_id="550e8400-e29b-41d4-a716-446655440000",
            heart_rate=75.0,
            heart_rate_variability=42.5,
            activity_type="walking",
            activity_confidence=0.85,
            fall_detected=False,
            workout_active=True,
            recorded_at=datetime.now()
        )
        db.add(health_data)
        
        # Create some sample location data
        location_data = LocationData(
            officer_id="550e8400-e29b-41d4-a716-446655440000",
            latitude=40.7128,
            longitude=-74.0060,
            accuracy=5.0,
            horizontal_accuracy=5.0,
            recorded_at=datetime.now()
        )
        db.add(location_data)
        
        db.commit()
        print("✅ Sample data created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()
