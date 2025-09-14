"""
ML Integration Routes for Heart Rate Analysis
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from datetime import datetime
import json

from app.db import get_db
from app.models import Officer, HealthData, RiskEvent

# Import ML components (adjust path as needed)
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../ml'))

from features.heart_rate_features import HeartRateFeatureExtractor
from models.risk_assessment_model import RiskAssessmentModel

router = APIRouter()

# Initialize ML components
risk_model = RiskAssessmentModel()
officer_extractors = {}

# Load pre-trained model if available
try:
    risk_model.load_model("ml/models/risk_model.pkl")
    print("✅ Loaded pre-trained risk assessment model")
except:
    print("⚠️ No pre-trained model found - using rule-based fallback")

class HeartRateMLRequest:
    """Request for ML processing"""
    def __init__(self, officer_id: str, heart_rate: float, timestamp: str, 
                 confidence: float = 1.0, metadata: Optional[Dict] = None):
        self.officer_id = officer_id
        self.heart_rate = heart_rate
        self.timestamp = timestamp
        self.confidence = confidence
        self.metadata = metadata or {}

@router.post("/ml/heart-rate/process")
async def process_heart_rate_ml(
    officer_id: str,
    heart_rate: float,
    timestamp: str,
    confidence: float = 1.0,
    metadata: Optional[Dict] = None,
    db: Session = Depends(get_db)
):
    """
    Process heart rate data with ML and update officer risk
    """
    try:
        # Get or create officer
        officer = db.query(Officer).filter(Officer.id == officer_id).first()
        if not officer:
            raise HTTPException(status_code=404, detail="Officer not found")
        
        # Initialize feature extractor for officer if needed
        if officer_id not in officer_extractors:
            extractor = HeartRateFeatureExtractor(window_size=60, min_samples=10)
            # Set officer profile based on age (if available)
            age = 30  # Default age, should be stored in officer profile
            extractor.set_officer_profile(age=age)
            officer_extractors[officer_id] = extractor
        
        # Process heart rate data
        extractor = officer_extractors[officer_id]
        hr_timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        features = extractor.add_sample(heart_rate, hr_timestamp, confidence)
        
        # Get risk assessment
        risk_prediction = risk_model.predict_risk(features)
        
        # Update officer risk level
        officer.current_risk_level = risk_prediction.risk_level
        officer.current_risk_score = risk_prediction.risk_score
        officer.last_seen = datetime.utcnow()
        
        # Create health data record
        health_data = HealthData(
            officer_id=officer_id,
            timestamp=hr_timestamp,
            heart_rate=heart_rate,
            activity_type=features.intensity_zone,
            fall_detected=False,  # This would come from motion sensors
            motion_x=metadata.get('motion_x') if metadata else None,
            motion_y=metadata.get('motion_y') if metadata else None,
            motion_z=metadata.get('motion_z') if metadata else None
        )
        db.add(health_data)
        
        # Create risk event if risk level is elevated
        if risk_prediction.risk_level in ['medium', 'high', 'critical']:
            risk_event = RiskEvent(
                officer_id=officer_id,
                timestamp=hr_timestamp,
                risk_level=risk_prediction.risk_level,
                risk_score=risk_prediction.risk_score,
                description=f"ML Risk Assessment: {risk_prediction.risk_level}",
                recommendations=", ".join(risk_prediction.recommendations)
            )
            db.add(risk_event)
        
        db.commit()
        
        return {
            "officer_id": officer_id,
            "risk_level": risk_prediction.risk_level,
            "risk_score": risk_prediction.risk_score,
            "confidence": risk_prediction.confidence,
            "intensity_zone": features.intensity_zone,
            "intensity_percentage": features.intensity_percentage,
            "hr_anomaly_score": features.hr_anomaly_score,
            "stress_indicator": features.stress_indicator,
            "fatigue_indicator": features.fatigue_indicator,
            "recommendations": risk_prediction.recommendations,
            "timestamp": risk_prediction.timestamp.isoformat()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing heart rate: {str(e)}")

@router.get("/ml/heart-rate/features/{officer_id}")
async def get_ml_features(officer_id: str, db: Session = Depends(get_db)):
    """
    Get current ML features for an officer
    """
    try:
        # Check if officer exists
        officer = db.query(Officer).filter(Officer.id == officer_id).first()
        if not officer:
            raise HTTPException(status_code=404, detail="Officer not found")
        
        # Check if we have an extractor for this officer
        if officer_id not in officer_extractors:
            raise HTTPException(status_code=404, detail="No ML data available for this officer")
        
        extractor = officer_extractors[officer_id]
        if not extractor.hr_buffer:
            raise HTTPException(status_code=404, detail="No heart rate data available")
        
        # Get latest features
        features = extractor._extract_features()
        
        return {
            "officer_id": officer_id,
            "features": {
                "current_hr": features.current_hr,
                "mean_hr": features.mean_hr,
                "std_hr": features.std_hr,
                "intensity_zone": features.intensity_zone,
                "intensity_percentage": features.intensity_percentage,
                "hr_anomaly_score": features.hr_anomaly_score,
                "stress_indicator": features.stress_indicator,
                "fatigue_indicator": features.fatigue_indicator,
                "recent_activity": features.recent_activity,
                "time_since_start": features.time_since_start
            },
            "buffer_size": len(extractor.hr_buffer),
            "timestamp": features.timestamp.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting features: {str(e)}")

@router.get("/ml/heart-rate/model/status")
async def get_ml_model_status():
    """
    Get ML model status
    """
    return {
        "is_trained": risk_model.is_trained,
        "officers_tracked": len(officer_extractors),
        "feature_extractors": list(officer_extractors.keys()),
        "model_type": "Random Forest" if risk_model.is_trained else "Rule-based"
    }

@router.post("/ml/heart-rate/officer/profile")
async def set_ml_officer_profile(
    officer_id: str,
    age: int,
    resting_hr: Optional[float] = None,
    max_hr: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """
    Set officer profile for ML processing
    """
    try:
        # Check if officer exists
        officer = db.query(Officer).filter(Officer.id == officer_id).first()
        if not officer:
            raise HTTPException(status_code=404, detail="Officer not found")
        
        # Create or update extractor
        if officer_id in officer_extractors:
            extractor = officer_extractors[officer_id]
        else:
            extractor = HeartRateFeatureExtractor(window_size=60, min_samples=10)
            officer_extractors[officer_id] = extractor
        
        # Set officer profile
        extractor.set_officer_profile(age=age, resting_hr=resting_hr)
        
        return {
            "message": "Officer profile updated for ML processing",
            "officer_id": officer_id,
            "age": age,
            "resting_hr": resting_hr,
            "max_hr": max_hr or (220 - age)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error setting profile: {str(e)}")

@router.get("/ml/heart-rate/alerts")
async def get_ml_alerts(db: Session = Depends(get_db)):
    """
    Get current ML alerts for all officers
    """
    try:
        alerts = []
        
        for officer_id, extractor in officer_extractors.items():
            if len(extractor.hr_buffer) >= extractor.min_samples:
                features = extractor._extract_features()
                risk_prediction = risk_model.predict_risk(features)
                
                if risk_prediction.risk_level in ['high', 'critical']:
                    alerts.append({
                        "officer_id": officer_id,
                        "risk_level": risk_prediction.risk_level,
                        "risk_score": risk_prediction.risk_score,
                        "confidence": risk_prediction.confidence,
                        "recommendations": risk_prediction.recommendations,
                        "timestamp": risk_prediction.timestamp.isoformat()
                    })
        
        return {
            "alerts": alerts,
            "total_alerts": len(alerts),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting alerts: {str(e)}")
