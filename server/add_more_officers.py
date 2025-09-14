"""
Add More Sample Officers for Better Demo
This script adds additional officers with different risk levels and scenarios
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

def add_more_officers():
    """Add more officers with different scenarios"""
    
    officers_data = [
        {
            "badge_number": "PD004",
            "name": "Alex Rodriguez",
            "department": "Police Department",
            "phone": "+1-555-0104",
            "email": "alex.rodriguez@pd.gov",
            "risk_level": "critical",
            "risk_score": 0.95,
            "heart_rate": 150.0,
            "activity": "running",
            "latitude": 40.7614,
            "longitude": -73.9776,
            "scenario": "High-speed chase in progress"
        },
        {
            "badge_number": "FD005",
            "name": "Emma Wilson",
            "department": "Fire Department",
            "phone": "+1-555-0105",
            "email": "emma.wilson@fd.gov",
            "risk_level": "high",
            "risk_score": 0.80,
            "heart_rate": 110.0,
            "activity": "climbing",
            "latitude": 40.7505,
            "longitude": -73.9934,
            "scenario": "Fire rescue operation"
        },
        {
            "badge_number": "EMT006",
            "name": "David Chen",
            "department": "Emergency Medical",
            "phone": "+1-555-0106",
            "email": "david.chen@emt.gov",
            "risk_level": "medium",
            "risk_score": 0.55,
            "heart_rate": 90.0,
            "activity": "walking",
            "latitude": 40.7282,
            "longitude": -73.7949,
            "scenario": "Medical emergency response"
        },
        {
            "badge_number": "PD007",
            "name": "Lisa Martinez",
            "department": "Police Department",
            "phone": "+1-555-0107",
            "email": "lisa.martinez@pd.gov",
            "risk_level": "low",
            "risk_score": 0.15,
            "heart_rate": 68.0,
            "activity": "sitting",
            "latitude": 40.6892,
            "longitude": -74.0445,
            "scenario": "Desk duty - administrative work"
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
                
                # Add health data
                health_data = HealthData(
                    id=str(uuid.uuid4()),
                    officer_id=officer_id,
                    heart_rate=data["heart_rate"],
                    heart_rate_variability=45.0,
                    activity_type=data["activity"],
                    activity_confidence=0.9,
                    fall_detected=False,
                    fall_confidence=0.1,
                    workout_active=data["activity"] in ["running", "climbing"],
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
                    speed=3.0 if data["activity"] == "running" else 1.0,
                    course=180.0,
                    altitude=10.0,
                    recorded_at=datetime.utcnow() - timedelta(minutes=1)
                )
                
                db.add(location_data)
                
                # Add risk event
                risk_event = RiskEvent(
                    id=str(uuid.uuid4()),
                    officer_id=officer_id,
                    event_type="high_risk",
                    risk_level=data["risk_level"],
                    risk_score=data["risk_score"],
                    description=data["scenario"],
                    occurred_at=datetime.utcnow() - timedelta(minutes=5),
                    is_acknowledged=False,
                    is_resolved=False,
                    latitude=data["latitude"],
                    longitude=data["longitude"]
                )
                
                db.add(risk_event)
                
                print(f"✅ Added {data['name']} ({data['badge_number']}) - {data['risk_level'].upper()} risk - {data['scenario']}")
            
            db.commit()
            print(f"\n🎉 Successfully added {len(officers_data)} additional officers!")
            
        except Exception as e:
            db.rollback()
            print(f"❌ Error adding officers: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Adding More Sample Officers for Better Demo...")
    print("=" * 60)
    
    add_more_officers()
    
    print("\n📊 Additional officers added successfully!")
    print("You can now view them in the web dashboard at: http://localhost:3000")
    print("Or check the API at: http://localhost:8000/api/v1/ingest/officers")
