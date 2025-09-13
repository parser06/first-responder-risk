"""
Risk scoring endpoints for server-side risk calculation
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging
import uuid

from app.db import get_db
from app.schemas import RiskScoreRequest, RiskScoreResponse
from app.risk.scorer import RiskScorer

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/calculate", response_model=RiskScoreResponse)
async def calculate_risk_score(
    request: RiskScoreRequest,
    db: Session = Depends(get_db)
):
    """
    Calculate risk score for an officer based on current data
    """
    try:
        # Verify officer exists
        from app.models import Officer
        officer = db.query(Officer).filter(Officer.id == request.officer_id).first()
        if not officer:
            raise HTTPException(status_code=404, detail="Officer not found")
        
        # Calculate risk using the risk scorer
        risk_scorer = RiskScorer()
        risk_assessment = await risk_scorer.calculate_risk(
            officer_id=str(request.officer_id),
            health_data=request.health_data,
            location_data=request.location_data,
            db=db
        )
        
        return RiskScoreResponse(
            officer_id=request.officer_id,
            risk_score=risk_assessment["risk_score"],
            risk_level=risk_assessment["risk_level"],
            factors=risk_assessment["factors"],
            confidence=risk_assessment["confidence"],
            recommendations=risk_assessment["recommendations"],
            timestamp=risk_assessment["timestamp"]
        )
        
    except Exception as e:
        logger.error(f"Error calculating risk score: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/officers/{officer_id}/risk-history")
async def get_risk_history(
    officer_id: uuid.UUID,
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """
    Get risk history for an officer over the specified time period
    """
    try:
        from app.models import RiskEvent
        from datetime import datetime, timedelta
        
        # Verify officer exists
        from app.models import Officer
        officer = db.query(Officer).filter(Officer.id == officer_id).first()
        if not officer:
            raise HTTPException(status_code=404, detail="Officer not found")
        
        # Get risk events from the specified time period
        start_time = datetime.now() - timedelta(hours=hours)
        risk_events = db.query(RiskEvent).filter(
            RiskEvent.officer_id == officer_id,
            RiskEvent.occurred_at >= start_time
        ).order_by(RiskEvent.occurred_at.desc()).all()
        
        # Format response
        risk_history = []
        for event in risk_events:
            risk_history.append({
                "event_id": str(event.id),
                "event_type": event.event_type,
                "risk_level": event.risk_level,
                "risk_score": event.risk_score,
                "description": event.description,
                "occurred_at": event.occurred_at.isoformat(),
                "is_acknowledged": event.is_acknowledged,
                "is_resolved": event.is_resolved,
                "location": {
                    "latitude": event.latitude,
                    "longitude": event.longitude
                } if event.latitude and event.longitude else None
            })
        
        return {
            "officer_id": str(officer_id),
            "time_period_hours": hours,
            "total_events": len(risk_history),
            "risk_events": risk_history
        }
        
    except Exception as e:
        logger.error(f"Error getting risk history: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/officers/{officer_id}/current-risk")
async def get_current_risk(
    officer_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Get current risk status for an officer
    """
    try:
        from app.models import Officer
        
        # Get officer with current risk data
        officer = db.query(Officer).filter(Officer.id == officer_id).first()
        if not officer:
            raise HTTPException(status_code=404, detail="Officer not found")
        
        return {
            "officer_id": str(officer_id),
            "name": officer.name,
            "badge_number": officer.badge_number,
            "current_risk_level": officer.current_risk_level,
            "current_risk_score": officer.current_risk_score,
            "last_seen": officer.last_seen.isoformat(),
            "is_active": officer.is_active,
            "is_on_duty": officer.is_on_duty
        }
        
    except Exception as e:
        logger.error(f"Error getting current risk: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/risk-summary")
async def get_risk_summary(db: Session = Depends(get_db)):
    """
    Get overall risk summary for all active officers
    """
    try:
        from app.models import Officer
        from sqlalchemy import func
        
        # Get risk level counts
        risk_counts = db.query(
            Officer.current_risk_level,
            func.count(Officer.id).label('count')
        ).filter(
            Officer.is_active == True
        ).group_by(Officer.current_risk_level).all()
        
        # Format response
        summary = {
            "total_active_officers": sum(count for _, count in risk_counts),
            "risk_levels": {
                level: count for level, count in risk_counts
            },
            "high_risk_officers": next(
                (count for level, count in risk_counts if level == "high"), 0
            ),
            "medium_risk_officers": next(
                (count for level, count in risk_counts if level == "medium"), 0
            ),
            "low_risk_officers": next(
                (count for level, count in risk_counts if level == "low"), 0
            )
        }
        
        return summary
        
    except Exception as e:
        logger.error(f"Error getting risk summary: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
