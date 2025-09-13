"""
WebSocket endpoints for real-time communication
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
import logging
import json
import uuid
from typing import List

from app.db import get_db
from app.websocket_manager import websocket_manager

logger = logging.getLogger(__name__)
router = APIRouter()

@router.websocket("/live")
async def websocket_live_updates(websocket: WebSocket):
    """
    WebSocket endpoint for live officer monitoring updates
    """
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
                    try:
                        officer_uuid = uuid.UUID(officer_id)
                        await websocket_manager.subscribe_to_officer(websocket, officer_uuid)
                        await websocket_manager.send_personal_message({
                            "type": "subscription_confirmed",
                            "officer_id": officer_id,
                            "message": "Successfully subscribed to officer updates"
                        }, websocket)
                    except ValueError:
                        await websocket_manager.send_personal_message({
                            "type": "error",
                            "message": "Invalid officer ID format"
                        }, websocket)
                        
            elif message.get("type") == "unsubscribe":
                # Unsubscribe from specific officer updates
                officer_id = message.get("officer_id")
                if officer_id:
                    try:
                        officer_uuid = uuid.UUID(officer_id)
                        await websocket_manager.unsubscribe_from_officer(websocket, officer_uuid)
                        await websocket_manager.send_personal_message({
                            "type": "unsubscription_confirmed",
                            "officer_id": officer_id,
                            "message": "Successfully unsubscribed from officer updates"
                        }, websocket)
                    except ValueError:
                        await websocket_manager.send_personal_message({
                            "type": "error",
                            "message": "Invalid officer ID format"
                        }, websocket)
                        
            elif message.get("type") == "get_status":
                # Get current connection status
                status = websocket_manager.get_connection_stats()
                await websocket_manager.send_personal_message({
                    "type": "status",
                    "data": status
                }, websocket)
                
            else:
                await websocket_manager.send_personal_message({
                    "type": "error",
                    "message": f"Unknown message type: {message.get('type')}"
                }, websocket)
                
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        websocket_manager.disconnect(websocket)

@router.get("/connections")
async def get_connection_info():
    """
    Get information about active WebSocket connections
    """
    try:
        stats = websocket_manager.get_connection_stats()
        return {
            "active_connections": stats["total_connections"],
            "officer_subscriptions": stats["officer_subscriptions"],
            "subscribed_officers": [str(officer_id) for officer_id in stats["subscribed_officers"]],
            "connection_details": stats["connection_details"]
        }
    except Exception as e:
        logger.error(f"Error getting connection info: {e}")
        return {"error": "Failed to get connection information"}

@router.post("/broadcast")
async def broadcast_message(message: dict):
    """
    Broadcast a message to all connected WebSocket clients
    """
    try:
        await websocket_manager.send_broadcast(message)
        return {"success": True, "message": "Message broadcasted successfully"}
    except Exception as e:
        logger.error(f"Error broadcasting message: {e}")
        return {"success": False, "error": str(e)}

@router.post("/officer-update/{officer_id}")
async def send_officer_update(officer_id: str, update_data: dict):
    """
    Send an update for a specific officer to all subscribers
    """
    try:
        officer_uuid = uuid.UUID(officer_id)
        await websocket_manager.send_officer_update(officer_uuid, update_data)
        return {"success": True, "message": f"Officer update sent for {officer_id}"}
    except ValueError:
        return {"success": False, "error": "Invalid officer ID format"}
    except Exception as e:
        logger.error(f"Error sending officer update: {e}")
        return {"success": False, "error": str(e)}
