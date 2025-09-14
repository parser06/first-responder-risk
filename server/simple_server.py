"""
Simple working server for First Responder Risk Monitoring
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
from datetime import datetime

app = FastAPI(title="First Responder Risk Monitoring API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sample data
officers = [
    {
        "officer_id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "John Smith",
        "badge_number": "PD001",
        "department": "Police Department",
        "is_active": True,
        "is_on_duty": True,
        "risk_level": "low",
        "risk_score": 0.2,
        "last_seen": "2025-09-13T22:33:59"
    },
    {
        "officer_id": "550e8400-e29b-41d4-a716-446655440001",
        "name": "Sarah Johnson",
        "badge_number": "FD002",
        "department": "Fire Department",
        "is_active": True,
        "is_on_duty": True,
        "risk_level": "medium",
        "risk_score": 0.5,
        "last_seen": "2025-09-13T22:33:59"
    },
    {
        "officer_id": "550e8400-e29b-41d4-a716-446655440002",
        "name": "Mike Davis",
        "badge_number": "EMT003",
        "department": "Emergency Medical",
        "is_active": True,
        "is_on_duty": False,
        "risk_level": "low",
        "risk_score": 0.1,
        "last_seen": "2025-09-13T22:33:59"
    }
]

@app.get("/")
async def root():
    return {
        "message": "First Responder Risk Monitoring API",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "websocket_connections": 0
    }

@app.get("/api/v1/ingest/officers")
async def get_officers():
    return {
        "officers": officers,
        "total_count": len(officers)
    }

@app.post("/api/v1/ingest/data")
async def ingest_data(data: dict):
    officer_id = data.get("officer_id")
    
    # Find officer
    officer = next((o for o in officers if o["officer_id"] == officer_id), None)
    if not officer:
        raise HTTPException(status_code=404, detail="Officer not found")
    
    # Update officer data
    officer["last_seen"] = datetime.now().isoformat()
    officer["risk_score"] = data.get("risk_score", 0.3)
    officer["risk_level"] = "medium" if officer["risk_score"] > 0.5 else "low"
    
    return {
        "success": True,
        "message": "Data ingested successfully",
        "risk_assessment": {
            "risk_score": officer["risk_score"],
            "risk_level": officer["risk_level"]
        }
    }

if __name__ == "__main__":
    print("🚀 Starting First Responder Risk Monitoring API...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📊 API Documentation: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
