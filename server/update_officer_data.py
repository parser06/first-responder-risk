"""
Update Officer Data with Realistic Information
This script updates existing officers with more detailed health and location data
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

def update_officer_data():
    """Update existing officers with realistic data"""
    
    # Initialize database
    init_db()
    
    with Session(engine) as db:
        try:
            # Get existing officers
            officers = db.query(Officer).all()
            
            for officer in officers:
                print(f"Updating {officer.name} ({officer.badge_number})...")
                
                # Update officer with realistic risk data
                if officer.badge_number == "PD001":  # John Smith - Medium Risk
                    officer.current_risk_level = "medium"
                    officer.current_risk_score = 0.65
                    officer.is_on_duty = True
                    heart_rate = 85.0
                    activity = "walking"
                    lat, lon = 40.7128, -74.0060
                    risk_desc = "Elevated heart rate during routine patrol"
                    
                elif officer.badge_number == "FD002":  # Sarah Johnson - High Risk
                    officer.current_risk_level = "high"
                    officer.current_risk_score = 0.85
                    officer.is_on_duty = True
                    heart_rate = 120.0
                    activity = "running"
                    lat, lon = 40.7589, -73.9851
                    risk_desc = "High intensity activity - emergency response"
                    
                elif officer.badge_number == "EMT003":  # Mike Davis - Low Risk
                    officer.current_risk_level = "low"
                    officer.current_risk_score = 0.25
                    officer.is_on_duty = False
                    heart_rate = 72.0
                    activity = "standing"
                    lat, lon = 40.7505, -73.9934
                    risk_desc = "Normal vital signs - off duty"
                
                # Update last seen
                officer.last_seen = datetime.utcnow() - timedelta(minutes=1)
                
                # Add fresh health data
                health_data = HealthData(
                    id=str(uuid.uuid4()),
                    officer_id=officer.id,
                    heart_rate=heart_rate,
                    heart_rate_variability=45.0,
                    activity_type=activity,
                    activity_confidence=0.8,
                    fall_detected=False,
                    fall_confidence=0.1,
                    workout_active=activity == "running",
                    recorded_at=datetime.utcnow() - timedelta(minutes=1)
                )
                
                db.add(health_data)
                
                # Add fresh location data
                location_data = LocationData(
                    id=str(uuid.uuid4()),
                    officer_id=officer.id,
                    latitude=lat,
                    longitude=lon,
                    accuracy=5.0,
                    speed=2.0 if activity == "walking" else 0.0,
                    course=180.0,
                    altitude=10.0,
                    recorded_at=datetime.utcnow() - timedelta(minutes=1)
                )
                
                db.add(location_data)
                
                # Add fresh risk event
                risk_event = RiskEvent(
                    id=str(uuid.uuid4()),
                    officer_id=officer.id,
                    event_type="high_risk",
                    risk_level=officer.current_risk_level,
                    risk_score=officer.current_risk_score,
                    description=risk_desc,
                    occurred_at=datetime.utcnow() - timedelta(minutes=5),
                    is_acknowledged=False,
                    is_resolved=False,
                    latitude=lat,
                    longitude=lon
                )
                
                db.add(risk_event)
                
                print(f"  ✅ Updated {officer.name}: {officer.current_risk_level.upper()} risk, HR={heart_rate} BPM, {activity}")
            
            db.commit()
            print(f"\n🎉 Successfully updated {len(officers)} officers with realistic data!")
            
        except Exception as e:
            db.rollback()
            print(f"❌ Error updating officers: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Updating Officer Data with Realistic Information...")
    print("=" * 60)
    
    update_officer_data()
    
    print("\n📊 Officers updated successfully!")
    print("You can now view them in the web dashboard at: http://localhost:3000")
    print("Or check the API at: http://localhost:8000/api/v1/ingest/officers")
