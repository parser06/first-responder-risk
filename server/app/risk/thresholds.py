"""
Risk thresholds and configuration for the scoring system
"""

from enum import Enum
from typing import Dict, Any

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class RiskThresholds:
    """Configuration for risk assessment thresholds"""
    
    # Risk score thresholds
    HIGH_RISK_THRESHOLD = 0.7
    MEDIUM_RISK_THRESHOLD = 0.4
    LOW_RISK_THRESHOLD = 0.0
    
    # Heart rate thresholds (BPM)
    HEART_RATE = {
        "very_low": 50,
        "low": 60,
        "normal_max": 100,
        "elevated": 150,
        "high": 180
    }
    
    # Heart rate variability thresholds (RMSSD in ms)
    HRV = {
        "very_low": 15,
        "low": 20,
        "normal_min": 20,
        "normal_max": 50,
        "high": 50
    }
    
    # Motion thresholds (g-force)
    MOTION = {
        "very_low": 0.5,
        "low": 1.0,
        "normal_max": 3.0,
        "high": 6.0
    }
    
    # Location accuracy threshold (meters)
    LOCATION_ACCURACY_THRESHOLD = 100.0
    
    # Activity confidence threshold
    ACTIVITY_CONFIDENCE_THRESHOLD = 0.5
    
    # Fall detection confidence threshold
    FALL_CONFIDENCE_THRESHOLD = 0.7

class RiskWeights:
    """Weights for different risk factors"""
    
    HEART_RATE = 0.25
    HEART_RATE_VARIABILITY = 0.20
    MOTION = 0.20
    FALL_DETECTION = 0.15
    ACTIVITY = 0.10
    LOCATION = 0.10
    HISTORICAL = 0.10

class ActivityRiskLevels:
    """Risk levels for different activity types"""
    
    ACTIVITY_RISK = {
        "stationary": 0.0,
        "walking": 0.1,
        "running": 0.3,
        "cycling": 0.2,
        "driving": 0.1,
        "unknown": 0.5
    }

def get_risk_level(score: float) -> RiskLevel:
    """Determine risk level based on score"""
    if score >= RiskThresholds.HIGH_RISK_THRESHOLD:
        return RiskLevel.HIGH
    elif score >= RiskThresholds.MEDIUM_RISK_THRESHOLD:
        return RiskLevel.MEDIUM
    else:
        return RiskLevel.LOW

def get_risk_color(risk_level: RiskLevel) -> str:
    """Get color code for risk level display"""
    colors = {
        RiskLevel.LOW: "#22c55e",      # Green
        RiskLevel.MEDIUM: "#f59e0b",   # Yellow/Orange
        RiskLevel.HIGH: "#ef4444"      # Red
    }
    return colors.get(risk_level, "#6b7280")  # Gray as default

def get_risk_description(risk_level: RiskLevel) -> str:
    """Get human-readable description for risk level"""
    descriptions = {
        RiskLevel.LOW: "Low Risk - All systems normal",
        RiskLevel.MEDIUM: "Medium Risk - Monitor closely",
        RiskLevel.HIGH: "High Risk - Immediate attention required"
    }
    return descriptions.get(risk_level, "Unknown Risk Level")
