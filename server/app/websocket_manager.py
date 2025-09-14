"""
WebSocket connection manager for real-time officer monitoring
"""

import json
import asyncio
import logging
from typing import List, Dict, Any, Optional
from fastapi import WebSocket
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.officer_subscriptions: Dict[uuid.UUID, List[WebSocket]] = {}
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_metadata[websocket] = {
            "connected_at": datetime.now(),
            "subscribed_officers": set(),
            "last_ping": datetime.now()
        }
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            
            # Remove from officer subscriptions
            if websocket in self.connection_metadata:
                subscribed_officers = self.connection_metadata[websocket]["subscribed_officers"]
                for officer_id in subscribed_officers:
                    if officer_id in self.officer_subscriptions:
                        if websocket in self.officer_subscriptions[officer_id]:
                            self.officer_subscriptions[officer_id].remove(websocket)
                        if not self.officer_subscriptions[officer_id]:
                            del self.officer_subscriptions[officer_id]
                
                del self.connection_metadata[websocket]
            
            logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send a message to a specific WebSocket connection"""
        try:
            await websocket.send_text(json.dumps(message, default=str))
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def send_broadcast(self, message: Dict[str, Any]):
        """Send a message to all connected WebSockets"""
        if not self.active_connections:
            return
        
        message_text = json.dumps(message, default=str)
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_text)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
    
    async def send_to_officer_subscribers(self, officer_id: uuid.UUID, message: Dict[str, Any]):
        """Send a message to all WebSockets subscribed to a specific officer"""
        if officer_id not in self.officer_subscriptions:
            return
        
        message_text = json.dumps(message, default=str)
        disconnected = []
        
        for connection in self.officer_subscriptions[officer_id]:
            try:
                await connection.send_text(message_text)
            except Exception as e:
                logger.error(f"Error sending officer update: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
    
    async def subscribe_to_officer(self, websocket: WebSocket, officer_id: uuid.UUID):
        """Subscribe a WebSocket to updates for a specific officer"""
        if officer_id not in self.officer_subscriptions:
            self.officer_subscriptions[officer_id] = []
        
        if websocket not in self.officer_subscriptions[officer_id]:
            self.officer_subscriptions[officer_id].append(websocket)
            
            # Update connection metadata
            if websocket in self.connection_metadata:
                self.connection_metadata[websocket]["subscribed_officers"].add(officer_id)
            
            logger.info(f"WebSocket subscribed to officer {officer_id}")
    
    async def unsubscribe_from_officer(self, websocket: WebSocket, officer_id: uuid.UUID):
        """Unsubscribe a WebSocket from updates for a specific officer"""
        if officer_id in self.officer_subscriptions:
            if websocket in self.officer_subscriptions[officer_id]:
                self.officer_subscriptions[officer_id].remove(websocket)
                if not self.officer_subscriptions[officer_id]:
                    del self.officer_subscriptions[officer_id]
            
            # Update connection metadata
            if websocket in self.connection_metadata:
                self.connection_metadata[websocket]["subscribed_officers"].discard(officer_id)
            
            logger.info(f"WebSocket unsubscribed from officer {officer_id}")
    
    async def send_officer_update(self, officer_id: uuid.UUID, update_data: Dict[str, Any]):
        """Send an officer update to all subscribers"""
        message = {
            "type": "officer_update",
            "timestamp": datetime.now().isoformat(),
            "officer_id": str(officer_id),
            "data": update_data
        }
        await self.send_to_officer_subscribers(officer_id, message)
    
    async def send_risk_event(self, event_data: Dict[str, Any]):
        """Send a risk event alert to all connections"""
        message = {
            "type": "risk_event",
            "timestamp": datetime.now().isoformat(),
            "data": event_data
        }
        await self.send_broadcast(message)
    
    async def send_system_alert(self, alert_data: Dict[str, Any]):
        """Send a system-wide alert to all connections"""
        message = {
            "type": "system_alert",
            "timestamp": datetime.now().isoformat(),
            "data": alert_data
        }
        await self.send_broadcast(message)
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get statistics about active connections"""
        return {
            "total_connections": len(self.active_connections),
            "officer_subscriptions": len(self.officer_subscriptions),
            "subscribed_officers": list(self.officer_subscriptions.keys()),
            "connection_details": {
                str(i): {
                    "connected_at": metadata["connected_at"].isoformat(),
                    "subscribed_officers": list(metadata["subscribed_officers"]),
                    "last_ping": metadata["last_ping"].isoformat()
                }
                for i, (conn, metadata) in enumerate(self.connection_metadata.items())
            }
        }

# Global WebSocket manager instance
websocket_manager = WebSocketManager()
