"""
Simplified First Responder Risk Monitoring System - FastAPI Backend
Main application entry point without Redis dependency
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import json
from typing import List, Dict, Any
import logging

from app.config import settings
from app.db_simple import init_db
from app.routes import ingest, score, ws
from app.websocket_manager import WebSocketManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global WebSocket manager
websocket_manager = WebSocketManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting First Responder Risk Monitoring API")
    await init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down First Responder Risk Monitoring API")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Real-time monitoring system for first responders",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ingest.router, prefix="/api/v1/ingest", tags=["ingest"])
app.include_router(score.router, prefix="/api/v1/score", tags=["score"])
app.include_router(ws.router, prefix="/api/v1/ws", tags=["websocket"])

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "First Responder Risk Monitoring API",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "websocket_connections": len(websocket_manager.active_connections)
    }

# WebSocket endpoint for real-time updates
@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time officer monitoring"""
    await websocket_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "ping":
                await websocket_manager.send_personal_message({
                    "type": "pong",
                    "timestamp": message.get("timestamp")
                }, websocket)
            elif message.get("type") == "subscribe":
                # Subscribe to specific officer updates
                officer_id = message.get("officer_id")
                if officer_id:
                    await websocket_manager.subscribe_to_officer(websocket, officer_id)
                    
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
