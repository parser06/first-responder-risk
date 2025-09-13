"""
Pydantic schemas for API request/response validation
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class EventType(str, Enum):
    HIGH_RISK = "high_risk"
    FALL_DETECTED = "fall_detected"
    SOS = "sos"
    HEART_RATE_ANOMALY = "heart_rate_anomaly"
    MOTION_ANOMALY = "motion_anomaly"
    LOCATION_ANOMALY = "location_anomaly"

# Health Data Schemas
class HealthDataBase(BaseModel):
    heart_rate: Optional[float] = None
    heart_rate_variability: Optional[float] = None
    resting_heart_rate: Optional[float] = None
    acceleration_x: Optional[float] = None
    acceleration_y: Optional[float] = None
    acceleration_z: Optional[float] = None
    gyroscope_x: Optional[float] = None
    gyroscope_y: Optional[float] = None
    gyroscope_z: Optional[float] = None
    activity_type: Optional[str] = None
    activity_confidence: Optional[float] = None
    fall_detected: bool = False
    fall_confidence: Optional[float] = None
    workout_active: bool = False
    workout_duration: Optional[int] = None
    raw_sensor_data: Optional[Dict[str, Any]] = None

class HealthDataCreate(HealthDataBase):
    pass

class HealthData(HealthDataBase):
    id: uuid.UUID
    officer_id: uuid.UUID
    recorded_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True

# Location Data Schemas
class LocationDataBase(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    altitude: Optional[float] = None
    accuracy: Optional[float] = None
    horizontal_accuracy: Optional[float] = None
    vertical_accuracy: Optional[float] = None
    speed: Optional[float] = None
    course: Optional[float] = None
    course_accuracy: Optional[float] = None

class LocationDataCreate(LocationDataBase):
    pass

class LocationData(LocationDataBase):
    id: uuid.UUID
    officer_id: uuid.UUID
    recorded_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True

# Officer Schemas
class OfficerBase(BaseModel):
    badge_number: str
    name: str
    department: str
    phone: Optional[str] = None
    email: Optional[str] = None

class OfficerCreate(OfficerBase):
    device_id: str
    app_version: Optional[str] = None

class OfficerUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None
    is_on_duty: Optional[bool] = None

class Officer(OfficerBase):
    id: uuid.UUID
    is_active: bool
    is_on_duty: bool
    last_seen: datetime
    current_risk_level: RiskLevel
    current_risk_score: float
    device_id: str
    app_version: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Risk Event Schemas
class RiskEventBase(BaseModel):
    event_type: EventType
    risk_level: RiskLevel
    risk_score: float = Field(..., ge=0.0, le=1.0)
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class RiskEventCreate(RiskEventBase):
    pass

class RiskEvent(RiskEventBase):
    id: uuid.UUID
    officer_id: uuid.UUID
    is_acknowledged: bool
    is_resolved: bool
    acknowledged_by: Optional[str] = None
    resolved_by: Optional[str] = None
    occurred_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Data Ingestion Schemas
class SensorData(BaseModel):
    """Raw sensor data from Apple Watch"""
    heart_rate: Optional[float] = None
    heart_rate_variability: Optional[float] = None
    acceleration: Optional[Dict[str, float]] = None
    gyroscope: Optional[Dict[str, float]] = None
    activity_type: Optional[str] = None
    activity_confidence: Optional[float] = None
    fall_detected: bool = False
    fall_confidence: Optional[float] = None
    workout_active: bool = False
    workout_duration: Optional[int] = None

class LocationData(BaseModel):
    """GPS location data from iPhone"""
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    accuracy: Optional[float] = None
    horizontal_accuracy: Optional[float] = None
    vertical_accuracy: Optional[float] = None
    speed: Optional[float] = None
    course: Optional[float] = None
    course_accuracy: Optional[float] = None

class DataIngestionRequest(BaseModel):
    """Complete data ingestion request from mobile app"""
    officer_id: uuid.UUID
    device_id: str
    timestamp: datetime
    sensor_data: Optional[SensorData] = None
    location_data: Optional[LocationData] = None
    risk_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    risk_level: Optional[RiskLevel] = None
    battery_level: Optional[float] = Field(None, ge=0.0, le=1.0)
    network_status: Optional[str] = None

class DataIngestionResponse(BaseModel):
    """Response to data ingestion request"""
    success: bool
    message: str
    risk_assessment: Optional[Dict[str, Any]] = None
    alerts: Optional[List[Dict[str, Any]]] = None

# WebSocket Schemas
class WebSocketMessage(BaseModel):
    """Base WebSocket message"""
    type: str
    timestamp: datetime
    data: Optional[Dict[str, Any]] = None

class OfficerUpdateMessage(WebSocketMessage):
    """Officer status update message"""
    type: str = "officer_update"
    officer_id: uuid.UUID
    risk_level: RiskLevel
    risk_score: float
    location: Optional[LocationData] = None
    last_seen: datetime

class RiskEventMessage(WebSocketMessage):
    """Risk event alert message"""
    type: str = "risk_event"
    event_id: uuid.UUID
    officer_id: uuid.UUID
    event_type: EventType
    risk_level: RiskLevel
    description: str
    location: Optional[LocationData] = None

class SystemAlertMessage(WebSocketMessage):
    """System-wide alert message"""
    type: str = "system_alert"
    alert_id: uuid.UUID
    alert_type: str
    severity: str
    title: str
    message: str
    officer_id: Optional[uuid.UUID] = None

# Risk Scoring Schemas
class RiskScoreRequest(BaseModel):
    """Request for risk score calculation"""
    officer_id: uuid.UUID
    health_data: Optional[HealthDataBase] = None
    location_data: Optional[LocationDataBase] = None
    historical_data: Optional[Dict[str, Any]] = None

class RiskScoreResponse(BaseModel):
    """Risk score calculation response"""
    officer_id: uuid.UUID
    risk_score: float = Field(..., ge=0.0, le=1.0)
    risk_level: RiskLevel
    factors: Dict[str, float]
    confidence: float
    recommendations: List[str]
    timestamp: datetime
