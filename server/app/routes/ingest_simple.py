"""
Simplified data ingestion endpoints without Redis dependency
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import logging
import uuid
from datetime import datetime

from app.db_simple import get_db, get_redis
from app.models import Officer, HealthData, LocationData, RiskEvent
from app.schemas import (
    DataIngestionRequest, 
    DataIngestionResponse, 
    HealthDataCreate, 
    LocationDataCreate,
    RiskEventCreate
)
from app.websocket_manager import websocket_manager

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/data", response_model=DataIngestionResponse)
async def ingest_data(
    request: DataIngestionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    redis = Depends(get_redis)
):
    """
    Ingest health and location data from mobile devices
    """
    try:
        # Convert UUID string to string for comparison
        officer_id_str = str(request.officer_id)
        
        # Verify officer exists and is active
        officer = db.query(Officer).filter(Officer.id == officer_id_str).first()
        if not officer:
            raise HTTPException(status_code=404, detail="Officer not found")
        
        if not officer.is_active:
            raise HTTPException(status_code=400, detail="Officer is not active")
        
        # Verify device ID matches
        if officer.device_id != request.device_id:
            raise HTTPException(status_code=403, detail="Device ID mismatch")
        
        # Update officer last seen
        officer.last_seen = datetime.now()
        
        # Store health data if provided
        if request.sensor_data:
            health_data = HealthData(
                officer_id=officer_id_str,
                heart_rate=request.sensor_data.heart_rate,
                heart_rate_variability=request.sensor_data.heart_rate_variability,
                acceleration_x=request.sensor_data.acceleration.get("x") if request.sensor_data.acceleration else None,
                acceleration_y=request.sensor_data.acceleration.get("y") if request.sensor_data.acceleration else None,
                acceleration_z=request.sensor_data.acceleration.get("z") if request.sensor_data.acceleration else None,
                gyroscope_x=request.sensor_data.gyroscope.get("x") if request.sensor_data.gyroscope else None,
                gyroscope_y=request.sensor_data.gyroscope.get("y") if request.sensor_data.gyroscope else None,
                gyroscope_z=request.sensor_data.gyroscope.get("z") if request.sensor_data.gyroscope else None,
                activity_type=request.sensor_data.activity_type,
                activity_confidence=request.sensor_data.activity_confidence,
                fall_detected=request.sensor_data.fall_detected,
                fall_confidence=request.sensor_data.fall_confidence,
                workout_active=request.sensor_data.workout_active,
                workout_duration=request.sensor_data.workout_duration,
                raw_sensor_data=request.sensor_data.dict() if request.sensor_data else None,
                recorded_at=request.timestamp
            )
            db.add(health_data)
        
        # Store location data if provided
        if request.location_data:
            location_data = LocationData(
                officer_id=officer_id_str,
                latitude=request.location_data.latitude,
                longitude=request.location_data.longitude,
                altitude=request.location_data.altitude,
                accuracy=request.location_data.accuracy,
                horizontal_accuracy=request.location_data.horizontal_accuracy,
                vertical_accuracy=request.location_data.vertical_accuracy,
                speed=request.location_data.speed,
                course=request.location_data.course,
                course_accuracy=request.location_data.course_accuracy,
                recorded_at=request.timestamp
            )
            db.add(location_data)
        
        # Calculate risk score if not provided
        risk_score = request.risk_score
        risk_level = request.risk_level
        
        if risk_score is None or risk_level is None:
            # Simple risk calculation for demo
            risk_score = 0.3  # Default medium risk
            risk_level = "medium"
        
        # Update officer risk status
        officer.current_risk_score = risk_score
        officer.current_risk_level = risk_level.value if hasattr(risk_level, 'value') else risk_level
        
        # Check for risk events
        alerts = []
        if risk_level in ["high", "medium"] or (request.sensor_data and request.sensor_data.fall_detected):
            # Create risk event
            event_type = "fall_detected" if request.sensor_data and request.sensor_data.fall_detected else "high_risk"
            risk_event = RiskEvent(
                officer_id=officer_id_str,
                event_type=event_type,
                risk_level=risk_level.value if hasattr(risk_level, 'value') else risk_level,
                risk_score=risk_score,
                description=f"Risk level: {risk_level}",
                latitude=request.location_data.latitude if request.location_data else None,
                longitude=request.location_data.longitude if request.location_data else None,
                event_metadata={
                    "health_data": request.sensor_data.dict() if request.sensor_data else None,
                    "location_data": request.location_data.dict() if request.location_data else None,
                    "battery_level": request.battery_level,
                    "network_status": request.network_status
                }
            )
            db.add(risk_event)
            
            # Add to alerts
            alerts.append({
                "type": "risk_event",
                "officer_id": officer_id_str,
                "risk_level": risk_level,
                "description": f"Officer {officer.name} is at {risk_level} risk",
                "timestamp": request.timestamp.isoformat()
            })
        
        # Commit all changes
        db.commit()
        
        # Send real-time updates via WebSocket
        background_tasks.add_task(
            send_officer_update,
            officer_id_str,
            {
                "officer_id": officer_id_str,
                "name": officer.name,
                "badge_number": officer.badge_number,
                "risk_level": risk_level,
                "risk_score": risk_score,
                "last_seen": officer.last_seen.isoformat(),
                "location": {
                    "latitude": request.location_data.latitude if request.location_data else None,
                    "longitude": request.location_data.longitude if request.location_data else None,
                    "accuracy": request.location_data.accuracy if request.location_data else None
                } if request.location_data else None
            }
        )
        
        # Send risk event alerts if any
        if alerts:
            background_tasks.add_task(
                send_risk_alerts,
                alerts
            )
        
        return DataIngestionResponse(
            success=True,
            message="Data ingested successfully",
            risk_assessment={
                "risk_score": risk_score,
                "risk_level": risk_level,
                "factors": {
                    "heart_rate": request.sensor_data.heart_rate if request.sensor_data else None,
                    "motion": request.sensor_data.acceleration if request.sensor_data else None,
                    "location": request.location_data.dict() if request.location_data else None
                }
            },
            alerts=alerts
        )
        
    except Exception as e:
        logger.error(f"Error ingesting data: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

async def send_officer_update(officer_id: str, officer_status: dict):
    """Send officer update via WebSocket"""
    try:
        await websocket_manager.send_officer_update(officer_id, officer_status)
    except Exception as e:
        logger.error(f"Error sending officer update: {e}")

async def send_risk_alerts(alerts: List[dict]):
    """Send risk alerts via WebSocket"""
    try:
        for alert in alerts:
            await websocket_manager.send_risk_event(alert)
    except Exception as e:
        logger.error(f"Error sending risk alerts: {e}")

@router.get("/officers")
async def get_all_officers(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get all officers with their current status"""
    try:
        query = db.query(Officer)
        if active_only:
            query = query.filter(Officer.is_active == True)
        
        officers = query.all()
        
        officer_list = []
        for officer in officers:
            officer_list.append({
                "officer_id": str(officer.id),
                "name": officer.name,
                "badge_number": officer.badge_number,
                "department": officer.department,
                "is_active": officer.is_active,
                "is_on_duty": officer.is_on_duty,
                "risk_level": officer.current_risk_level,
                "risk_score": officer.current_risk_score,
                "last_seen": officer.last_seen.isoformat()
            })
        
        return {
            "officers": officer_list,
            "total_count": len(officer_list)
        }
        
    except Exception as e:
        logger.error(f"Error getting officers: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
