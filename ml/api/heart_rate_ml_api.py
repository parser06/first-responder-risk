"""
Real-time Heart Rate ML API
Integrates with the main FastAPI server for real-time risk assessment
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
import asyncio
import json

from ..features.heart_rate_features import HeartRateFeatureExtractor, HeartRateFeatures
from ..models.risk_assessment_model import RiskAssessmentModel, RiskPrediction

# Initialize components
feature_extractor = HeartRateFeatureExtractor(window_size=60, min_samples=10)
risk_model = RiskAssessmentModel()

# Load pre-trained model if available
try:
    risk_model.load_model("ml/models/risk_model.pkl")
    print("✅ Loaded pre-trained risk assessment model")
except:
    print("⚠️ No pre-trained model found - using rule-based fallback")

router = APIRouter()

class HeartRateData(BaseModel):
    """Heart rate data from Apple Watch"""
    officer_id: str
    heart_rate: float
    timestamp: str
    confidence: float = 1.0
    source: str = "watch"
    metadata: Optional[Dict] = None

class RiskAssessmentRequest(BaseModel):
    """Request for risk assessment"""
    officer_id: str
    heart_rate_data: List[HeartRateData]
    officer_profile: Optional[Dict] = None

class RiskAssessmentResponse(BaseModel):
    """Risk assessment response"""
    officer_id: str
    risk_level: str
    risk_score: float
    confidence: float
    contributing_factors: Dict[str, float]
    recommendations: List[str]
    timestamp: str
    features: Dict

# Store officer profiles and feature extractors
officer_profiles = {}
officer_extractors = {}

@router.post("/heart-rate/process", response_model=RiskAssessmentResponse)
async def process_heart_rate_data(request: RiskAssessmentRequest):
    """
    Process real-time heart rate data and return risk assessment
    """
    try:
        officer_id = request.officer_id
        
        # Initialize officer profile if not exists
        if officer_id not in officer_profiles:
            profile = request.officer_profile or {}
            officer_profiles[officer_id] = {
                'age': profile.get('age', 30),
                'resting_hr': profile.get('resting_hr', None),
                'max_hr': profile.get('max_hr', None)
            }
            
            # Create feature extractor for this officer
            extractor = HeartRateFeatureExtractor(window_size=60, min_samples=10)
            extractor.set_officer_profile(
                age=officer_profiles[officer_id]['age'],
                resting_hr=officer_profiles[officer_id]['resting_hr']
            )
            officer_extractors[officer_id] = extractor
        
        # Process each heart rate sample
        extractor = officer_extractors[officer_id]
        latest_features = None
        
        for hr_data in request.heart_rate_data:
            timestamp = datetime.fromisoformat(hr_data.timestamp.replace('Z', '+00:00'))
            features = extractor.add_sample(
                hr_data.heart_rate,
                timestamp,
                hr_data.confidence
            )
            latest_features = features
        
        if not latest_features:
            raise HTTPException(status_code=400, detail="No valid heart rate data provided")
        
        # Get risk assessment
        risk_prediction = risk_model.predict_risk(latest_features)
        
        # Convert features to dictionary for response
        features_dict = {
            'current_hr': latest_features.current_hr,
            'mean_hr': latest_features.mean_hr,
            'std_hr': latest_features.std_hr,
            'intensity_zone': latest_features.intensity_zone,
            'intensity_percentage': latest_features.intensity_percentage,
            'hr_anomaly_score': latest_features.hr_anomaly_score,
            'stress_indicator': latest_features.stress_indicator,
            'fatigue_indicator': latest_features.fatigue_indicator,
            'recent_activity': latest_features.recent_activity,
            'time_since_start': latest_features.time_since_start
        }
        
        return RiskAssessmentResponse(
            officer_id=officer_id,
            risk_level=risk_prediction.risk_level,
            risk_score=risk_prediction.risk_score,
            confidence=risk_prediction.confidence,
            contributing_factors=risk_prediction.contributing_factors,
            recommendations=risk_prediction.recommendations,
            timestamp=risk_prediction.timestamp.isoformat(),
            features=features_dict
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing heart rate data: {str(e)}")

@router.post("/heart-rate/single")
async def process_single_heart_rate(hr_data: HeartRateData):
    """
    Process a single heart rate measurement
    """
    try:
        officer_id = hr_data.officer_id
        
        # Initialize if needed
        if officer_id not in officer_extractors:
            extractor = HeartRateFeatureExtractor(window_size=60, min_samples=10)
            extractor.set_officer_profile(age=30)  # Default age
            officer_extractors[officer_id] = extractor
        
        # Process the single sample
        extractor = officer_extractors[officer_id]
        timestamp = datetime.fromisoformat(hr_data.timestamp.replace('Z', '+00:00'))
        features = extractor.add_sample(
            hr_data.heart_rate,
            timestamp,
            hr_data.confidence
        )
        
        # Get risk assessment
        risk_prediction = risk_model.predict_risk(features)
        
        return {
            'officer_id': officer_id,
            'heart_rate': hr_data.heart_rate,
            'risk_level': risk_prediction.risk_level,
            'risk_score': risk_prediction.risk_score,
            'confidence': risk_prediction.confidence,
            'intensity_zone': features.intensity_zone,
            'recommendations': risk_prediction.recommendations,
            'timestamp': risk_prediction.timestamp.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing heart rate: {str(e)}")

@router.get("/heart-rate/features/{officer_id}")
async def get_officer_features(officer_id: str):
    """
    Get current features for an officer
    """
    if officer_id not in officer_extractors:
        raise HTTPException(status_code=404, detail="Officer not found")
    
    extractor = officer_extractors[officer_id]
    if not extractor.hr_buffer:
        raise HTTPException(status_code=404, detail="No heart rate data available")
    
    # Get latest features
    latest_features = extractor._extract_features()
    
    return {
        'officer_id': officer_id,
        'features': {
            'current_hr': latest_features.current_hr,
            'mean_hr': latest_features.mean_hr,
            'std_hr': latest_features.std_hr,
            'intensity_zone': latest_features.intensity_zone,
            'intensity_percentage': latest_features.intensity_percentage,
            'hr_anomaly_score': latest_features.hr_anomaly_score,
            'stress_indicator': latest_features.stress_indicator,
            'fatigue_indicator': latest_features.fatigue_indicator,
            'recent_activity': latest_features.recent_activity,
            'time_since_start': latest_features.time_since_start
        },
        'buffer_size': len(extractor.hr_buffer),
        'timestamp': latest_features.timestamp.isoformat()
    }

@router.post("/heart-rate/train")
async def train_model(training_data: Dict):
    """
    Train the risk assessment model with new data
    """
    try:
        features = training_data.get('features', [])
        labels = training_data.get('labels', [])
        
        if not features or not labels:
            raise HTTPException(status_code=400, detail="Training data required")
        
        # Train the model
        results = risk_model.train(features, labels)
        
        # Save the trained model
        risk_model.save_model("ml/models/risk_model.pkl")
        
        return {
            'message': 'Model trained successfully',
            'results': results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error training model: {str(e)}")

@router.get("/heart-rate/model/status")
async def get_model_status():
    """
    Get current model status
    """
    return {
        'is_trained': risk_model.is_trained,
        'officers_tracked': len(officer_extractors),
        'feature_extractors': list(officer_extractors.keys())
    }

@router.post("/heart-rate/officer/profile")
async def set_officer_profile(officer_id: str, profile: Dict):
    """
    Set officer profile for better risk assessment
    """
    try:
        officer_profiles[officer_id] = {
            'age': profile.get('age', 30),
            'resting_hr': profile.get('resting_hr', None),
            'max_hr': profile.get('max_hr', None)
        }
        
        # Update or create extractor
        if officer_id in officer_extractors:
            officer_extractors[officer_id].set_officer_profile(
                age=officer_profiles[officer_id]['age'],
                resting_hr=officer_profiles[officer_id]['resting_hr']
            )
        else:
            extractor = HeartRateFeatureExtractor(window_size=60, min_samples=10)
            extractor.set_officer_profile(
                age=officer_profiles[officer_id]['age'],
                resting_hr=officer_profiles[officer_id]['resting_hr']
            )
            officer_extractors[officer_id] = extractor
        
        return {
            'message': 'Officer profile updated',
            'officer_id': officer_id,
            'profile': officer_profiles[officer_id]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error setting profile: {str(e)}")
