"""
SQLAlchemy models for the First Responder Risk Monitoring system (SQLite compatible)
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from datetime import datetime

from app.db_simple import Base

class Officer(Base):
    """Officer information and status"""
    __tablename__ = "officers"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    badge_number = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)
    phone = Column(String(20))
    email = Column(String(100))
    
    # Status
    is_active = Column(Boolean, default=False)
    is_on_duty = Column(Boolean, default=False)
    last_seen = Column(DateTime, default=func.now())
    
    # Current risk level
    current_risk_level = Column(String(20), default="low")  # low, medium, high
    current_risk_score = Column(Float, default=0.0)
    
    # Device information
    device_id = Column(String(100), unique=True)
    app_version = Column(String(20))
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    health_data = relationship("HealthData", back_populates="officer", cascade="all, delete-orphan")
    location_data = relationship("LocationData", back_populates="officer", cascade="all, delete-orphan")
    risk_events = relationship("RiskEvent", back_populates="officer", cascade="all, delete-orphan")

class HealthData(Base):
    """Health sensor data from Apple Watch"""
    __tablename__ = "health_data"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    officer_id = Column(String(36), ForeignKey("officers.id"), nullable=False)
    
    # Heart rate data
    heart_rate = Column(Float)
    heart_rate_variability = Column(Float)  # RMSSD in milliseconds
    resting_heart_rate = Column(Float)
    
    # Motion data
    acceleration_x = Column(Float)
    acceleration_y = Column(Float)
    acceleration_z = Column(Float)
    gyroscope_x = Column(Float)
    gyroscope_y = Column(Float)
    gyroscope_z = Column(Float)
    
    # Activity data
    activity_type = Column(String(50))  # walking, running, stationary, etc.
    activity_confidence = Column(Float)
    
    # Fall detection
    fall_detected = Column(Boolean, default=False)
    fall_confidence = Column(Float)
    
    # Workout data
    workout_active = Column(Boolean, default=False)
    workout_duration = Column(Integer)  # seconds
    
    # Raw sensor data (JSON)
    raw_sensor_data = Column(JSON)
    
    # Timestamps
    recorded_at = Column(DateTime, default=func.now(), index=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    officer = relationship("Officer", back_populates="health_data")

class LocationData(Base):
    """GPS location data from iPhone"""
    __tablename__ = "location_data"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    officer_id = Column(String(36), ForeignKey("officers.id"), nullable=False)
    
    # Location coordinates
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude = Column(Float)
    
    # Location accuracy
    accuracy = Column(Float)  # meters
    horizontal_accuracy = Column(Float)  # meters
    vertical_accuracy = Column(Float)  # meters
    
    # Movement data
    speed = Column(Float)  # m/s
    course = Column(Float)  # degrees
    course_accuracy = Column(Float)  # degrees
    
    # Timestamps
    recorded_at = Column(DateTime, default=func.now(), index=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    officer = relationship("Officer", back_populates="location_data")

class RiskEvent(Base):
    """Risk events and alerts"""
    __tablename__ = "risk_events"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    officer_id = Column(String(36), ForeignKey("officers.id"), nullable=False)
    
    # Event details
    event_type = Column(String(50), nullable=False)  # high_risk, fall_detected, sos, etc.
    risk_level = Column(String(20), nullable=False)  # low, medium, high
    risk_score = Column(Float, nullable=False)
    
    # Event data
    description = Column(Text)
    event_metadata = Column(JSON)  # Additional event-specific data (renamed from metadata)
    
    # Location at time of event
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Status
    is_acknowledged = Column(Boolean, default=False)
    is_resolved = Column(Boolean, default=False)
    acknowledged_by = Column(String(100))
    resolved_by = Column(String(100))
    
    # Timestamps
    occurred_at = Column(DateTime, default=func.now(), index=True)
    acknowledged_at = Column(DateTime)
    resolved_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    officer = relationship("Officer", back_populates="risk_events")

class SystemAlert(Base):
    """System-wide alerts and notifications"""
    __tablename__ = "system_alerts"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Alert details
    alert_type = Column(String(50), nullable=False)  # officer_down, system_error, etc.
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    
    # Related data
    officer_id = Column(String(36), ForeignKey("officers.id"))
    risk_event_id = Column(String(36), ForeignKey("risk_events.id"))
    
    # Status
    is_active = Column(Boolean, default=True)
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String(100))
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), index=True)
    acknowledged_at = Column(DateTime)
    
    # Relationships
    officer = relationship("Officer")
    risk_event = relationship("RiskEvent")
