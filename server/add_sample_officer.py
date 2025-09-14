"""
Add Sample Officer to Database
This script adds a sample officer with all their data to the SQLite database
"""

import os
import sys
import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Add the server directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db_simple import engine, init_db
from app.models import Officer, HealthData, LocationData, RiskEvent

def add_multiple_sample_officers():
    """Add multiple sample officers with different risk levels"""
    
    officers_data = [
        {
            "badge_number": "PD001",
            "name": "John Smith",
            "department": "Police Department",
            "phone": "+1-555-0101",
            "email": "john.smith@pd.gov",
            "risk_level": "medium",
            "risk_score": 0.65,
            "heart_rate": 85.0,
            "activity": "walking",
            "latitude": 40.7128,
            "longitude": -74.0060
        },
        {
            "badge_number": "FD002",
            "name": "Sarah Johnson",
            "department": "Fire Department",
            "phone": "+1-555-0102",
            "email": "sarah.johnson@fd.gov",
            "risk_level": "high",
            "risk_score": 0.85,
            "heart_rate": 120.0,
            "activity": "running",
            "latitude": 40.7589,
            "longitude": -73.9851
        },
        {
            "badge_number": "EMT003",
            "name": "Mike Davis",
            "department": "Emergency Medical",
            "phone": "+1-555-0103",
            "email": "mike.davis@emt.gov",
            "risk_level": "low",
            "risk_score": 0.25,
            "heart_rate": 72.0,
            "activity": "standing",
            "latitude": 40.7505,
            "longitude": -73.9934
        }
    ]
    
    # Initialize database
    init_db()
    
    with Session(engine) as db:
        try:
            for data in officers_data:
                officer_id = str(uuid.uuid4())
                
                # Create officer
                officer = Officer(
                    id=officer_id,
                    badge_number=data["badge_number"],
                    name=data["name"],
                    department=data["department"],
                    phone=data["phone"],
                    email=data["email"],
                    is_active=True,
                    is_on_duty=True,
                    current_risk_level=data["risk_level"],
                    current_risk_score=data["risk_score"],
                    device_id=f"device_{data['badge_number']}",
                    app_version="1.0.0",
                    last_seen=datetime.utcnow() - timedelta(minutes=1)
                )
                
                db.add(officer)
                
                # Add health data (using correct field names)
                health_data = HealthData(
                    id=str(uuid.uuid4()),
                    officer_id=officer_id,
                    heart_rate=data["heart_rate"],
                    heart_rate_variability=45.0,
                    activity_type=data["activity"],
                    activity_confidence=0.8,
                    fall_detected=False,
                    fall_confidence=0.1,
                    workout_active=data["activity"] == "running",
                    recorded_at=datetime.utcnow() - timedelta(minutes=1)
                )
                
                db.add(health_data)
                
                # Add location data
                location_data = LocationData(
                    id=str(uuid.uuid4()),
                    officer_id=officer_id,
                    latitude=data["latitude"],
                    longitude=data["longitude"],
                    accuracy=5.0,
                    speed=2.0,
                    course=180.0,
                    altitude=10.0,
                    recorded_at=datetime.utcnow() - timedelta(minutes=1)
                )
                
                db.add(location_data)
                
                # Add risk event (using correct field names)
                risk_event = RiskEvent(
                    id=str(uuid.uuid4()),
                    officer_id=officer_id,
                    event_type="high_risk",
                    risk_level=data["risk_level"],
                    risk_score=data["risk_score"],
                    description=f"Risk assessment for {data['name']} - {data['activity']} activity",
                    occurred_at=datetime.utcnow() - timedelta(minutes=5),
                    is_acknowledged=False,
                    is_resolved=False,
                    latitude=data["latitude"],
                    longitude=data["longitude"]
                )
                
                db.add(risk_event)
                
                print(f"✅ Added {data['name']} ({data['badge_number']}) - Risk: {data['risk_level'].upper()}")
            
            db.commit()
            print(f"\n🎉 Successfully added {len(officers_data)} sample officers!")
            
        except Exception as e:
            db.rollback()
            print(f"❌ Error adding sample officers: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Adding Sample Officers to Database...")
    print("=" * 50)
    
    # Add multiple sample officers
    add_multiple_sample_officers()
    
    print("\n📊 Sample officers added successfully!")
    print("You can now view them in the web dashboard at: http://localhost:3000")
    print("Or check the API at: http://localhost:8000/api/v1/ingest/officers")
