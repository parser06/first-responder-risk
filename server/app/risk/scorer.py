"""
Risk scoring engine for first responder monitoring
"""

import logging
import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from app.models import HealthData, LocationData, Officer
from app.schemas import RiskLevel

logger = logging.getLogger(__name__)

class RiskScorer:
    """Calculates risk scores based on health and location data"""
    
    def __init__(self):
        self.high_risk_threshold = 0.7
        self.medium_risk_threshold = 0.4
        
        # Risk factors weights
        self.weights = {
            "heart_rate": 0.25,
            "heart_rate_variability": 0.20,
            "motion": 0.20,
            "fall_detection": 0.15,
            "activity": 0.10,
            "location": 0.10
        }
    
    async def calculate_risk(
        self,
        officer_id: str,
        health_data: Optional[Any] = None,
        location_data: Optional[Any] = None,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive risk score for an officer
        """
        try:
            risk_factors = {}
            total_score = 0.0
            
            # Heart Rate Analysis
            if health_data and health_data.heart_rate:
                hr_score = self._analyze_heart_rate(health_data.heart_rate)
                risk_factors["heart_rate"] = hr_score
                total_score += hr_score * self.weights["heart_rate"]
            
            # Heart Rate Variability Analysis
            if health_data and health_data.heart_rate_variability:
                hrv_score = self._analyze_hrv(health_data.heart_rate_variability)
                risk_factors["heart_rate_variability"] = hrv_score
                total_score += hrv_score * self.weights["heart_rate_variability"]
            
            # Motion Analysis
            if health_data and health_data.acceleration:
                motion_score = self._analyze_motion(health_data)
                risk_factors["motion"] = motion_score
                total_score += motion_score * self.weights["motion"]
            
            # Fall Detection
            if health_data and health_data.fall_detected:
                fall_score = 1.0  # Maximum risk for fall detection
                risk_factors["fall_detection"] = fall_score
                total_score += fall_score * self.weights["fall_detection"]
            else:
                risk_factors["fall_detection"] = 0.0
            
            # Activity Analysis
            if health_data and health_data.activity_type:
                activity_score = self._analyze_activity(health_data)
                risk_factors["activity"] = activity_score
                total_score += activity_score * self.weights["activity"]
            
            # Location Analysis
            if location_data:
                location_score = self._analyze_location(location_data, db, officer_id)
                risk_factors["location"] = location_score
                total_score += location_score * self.weights["location"]
            
            # Historical Context (if database available)
            if db:
                historical_score = self._analyze_historical_context(officer_id, db)
                risk_factors["historical"] = historical_score
                total_score += historical_score * 0.1  # 10% weight for historical context
            
            # Normalize score to 0-1 range
            total_score = min(max(total_score, 0.0), 1.0)
            
            # Determine risk level
            if total_score >= self.high_risk_threshold:
                risk_level = RiskLevel.HIGH
            elif total_score >= self.medium_risk_threshold:
                risk_level = RiskLevel.MEDIUM
            else:
                risk_level = RiskLevel.LOW
            
            return {
                "risk_score": total_score,
                "risk_level": risk_level,
                "factors": risk_factors,
                "confidence": self._calculate_confidence(risk_factors),
                "timestamp": datetime.now().isoformat(),
                "recommendations": self._generate_recommendations(risk_factors, total_score)
            }
            
        except Exception as e:
            logger.error(f"Error calculating risk score: {e}")
            return {
                "risk_score": 0.0,
                "risk_level": RiskLevel.LOW,
                "factors": {},
                "confidence": 0.0,
                "timestamp": datetime.now().isoformat(),
                "recommendations": ["Unable to calculate risk - using default values"]
            }
    
    def _analyze_heart_rate(self, heart_rate: float) -> float:
        """Analyze heart rate for risk indicators"""
        # Normal resting HR: 60-100 bpm
        # High stress/activity: 100-150 bpm
        # Dangerous: >150 bpm or <50 bpm
        
        if heart_rate < 50:
            return 0.8  # Very low HR - potential medical issue
        elif heart_rate < 60:
            return 0.3  # Low HR - monitor
        elif heart_rate <= 100:
            return 0.0  # Normal range
        elif heart_rate <= 150:
            return 0.4  # Elevated - could be stress or activity
        elif heart_rate <= 180:
            return 0.7  # High - concerning
        else:
            return 1.0  # Very high - dangerous
    
    def _analyze_hrv(self, hrv: float) -> float:
        """Analyze heart rate variability for stress indicators"""
        # Normal HRV: 20-50 ms (RMSSD)
        # Low HRV indicates stress, fatigue, or medical issues
        
        if hrv < 15:
            return 0.9  # Very low HRV - high stress/fatigue
        elif hrv < 20:
            return 0.7  # Low HRV - concerning
        elif hrv < 30:
            return 0.4  # Below average
        elif hrv <= 50:
            return 0.0  # Normal range
        else:
            return 0.2  # High HRV - generally good but could indicate irregular rhythm
    
    def _analyze_motion(self, health_data: Any) -> float:
        """Analyze motion patterns for unusual activity"""
        if not health_data.acceleration:
            return 0.0
        
        # Calculate motion magnitude
        accel = health_data.acceleration
        motion_magnitude = np.sqrt(
            accel.get("x", 0)**2 + 
            accel.get("y", 0)**2 + 
            accel.get("z", 0)**2
        )
        
        # Normal motion: 1-3 g (gravity units)
        # High motion: 3-6 g (running, jumping)
        # Very high motion: >6 g (potential impact, fall)
        
        if motion_magnitude < 0.5:
            return 0.6  # Very low motion - potential unconsciousness
        elif motion_magnitude < 1.0:
            return 0.3  # Low motion - stationary
        elif motion_magnitude <= 3.0:
            return 0.0  # Normal motion range
        elif motion_magnitude <= 6.0:
            return 0.4  # High motion - active
        else:
            return 0.8  # Very high motion - potential impact
    
    def _analyze_activity(self, health_data: Any) -> float:
        """Analyze activity type and confidence"""
        activity_type = health_data.activity_type
        confidence = health_data.activity_confidence or 0.0
        
        # Risk based on activity type
        activity_risk = {
            "stationary": 0.0,
            "walking": 0.1,
            "running": 0.3,
            "cycling": 0.2,
            "unknown": 0.5
        }.get(activity_type, 0.5)
        
        # Adjust based on confidence
        confidence_factor = 1.0 - (confidence or 0.0)
        
        return activity_risk * (1.0 + confidence_factor)
    
    def _analyze_location(self, location_data: Any, db: Optional[Session], officer_id: str) -> float:
        """Analyze location for risk factors"""
        if not location_data:
            return 0.0
        
        # Check location accuracy
        accuracy = location_data.accuracy or location_data.horizontal_accuracy
        if accuracy and accuracy > 100:  # >100m accuracy is unreliable
            return 0.3
        
        # Check for known high-risk areas (would need database lookup)
        # For now, return base risk
        return 0.0
    
    def _analyze_historical_context(self, officer_id: str, db: Session) -> float:
        """Analyze historical data for context"""
        try:
            # Get recent health data (last hour)
            recent_time = datetime.now() - timedelta(hours=1)
            recent_health = db.query(HealthData).filter(
                and_(
                    HealthData.officer_id == officer_id,
                    HealthData.recorded_at >= recent_time
                )
            ).order_by(desc(HealthData.recorded_at)).limit(10).all()
            
            if not recent_health:
                return 0.0
            
            # Analyze trends
            heart_rates = [h.heart_rate for h in recent_health if h.heart_rate]
            if len(heart_rates) > 3:
                hr_trend = np.polyfit(range(len(heart_rates)), heart_rates, 1)[0]
                if hr_trend > 5:  # Increasing HR trend
                    return 0.3
                elif hr_trend < -5:  # Decreasing HR trend
                    return 0.2
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error analyzing historical context: {e}")
            return 0.0
    
    def _calculate_confidence(self, factors: Dict[str, float]) -> float:
        """Calculate confidence in the risk assessment"""
        if not factors:
            return 0.0
        
        # Confidence based on number of available factors and their consistency
        available_factors = len([f for f in factors.values() if f is not None])
        max_factors = len(self.weights)
        
        factor_availability = available_factors / max_factors
        
        # Consistency check (factors pointing in same direction)
        if available_factors > 1:
            factor_values = [f for f in factors.values() if f is not None]
            consistency = 1.0 - np.std(factor_values) if len(factor_values) > 1 else 1.0
        else:
            consistency = 0.5
        
        return (factor_availability + consistency) / 2.0
    
    def _generate_recommendations(self, factors: Dict[str, float], total_score: float) -> list:
        """Generate recommendations based on risk factors"""
        recommendations = []
        
        if total_score >= self.high_risk_threshold:
            recommendations.append("IMMEDIATE ATTENTION REQUIRED - High risk detected")
        
        if factors.get("heart_rate", 0) > 0.7:
            recommendations.append("Monitor heart rate - elevated levels detected")
        
        if factors.get("heart_rate_variability", 0) > 0.7:
            recommendations.append("Check officer stress levels - low HRV detected")
        
        if factors.get("motion", 0) > 0.7:
            recommendations.append("Unusual motion patterns detected - check officer status")
        
        if factors.get("fall_detection", 0) > 0.5:
            recommendations.append("FALL DETECTED - Immediate response required")
        
        if factors.get("activity", 0) > 0.5:
            recommendations.append("High activity levels - monitor for fatigue")
        
        if not recommendations:
            recommendations.append("All systems normal - continue monitoring")
        
        return recommendations
