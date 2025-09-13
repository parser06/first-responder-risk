# Data Contracts - First Responder Risk Monitoring System

## Overview

This document defines the data contracts and API schemas for the First Responder Risk Monitoring System. All data exchange between components follows these standardized formats.

## API Base URLs

- **Development**: `http://localhost:8000/api/v1`
- **WebSocket**: `ws://localhost:8000/ws/live`
- **Web Dashboard**: `http://localhost:3000`

## Authentication

### JWT Token Format
```json
{
  "sub": "officer_id",
  "device_id": "device_identifier",
  "exp": 1234567890,
  "iat": 1234567890
}
```

## Data Ingestion API

### POST /ingest/data

**Request Body:**
```json
{
  "officer_id": "uuid",
  "device_id": "string",
  "timestamp": "2024-01-01T12:00:00Z",
  "sensor_data": {
    "heart_rate": 75.0,
    "heart_rate_variability": 42.5,
    "acceleration": {
      "x": 0.1,
      "y": -0.2,
      "z": 9.8
    },
    "gyroscope": {
      "x": 0.05,
      "y": 0.02,
      "z": -0.01
    },
    "activity_type": "walking",
    "activity_confidence": 0.85,
    "fall_detected": false,
    "fall_confidence": 0.0,
    "workout_active": true,
    "workout_duration": 1800
  },
  "location_data": {
    "latitude": 40.7128,
    "longitude": -74.0060,
    "altitude": 10.5,
    "accuracy": 5.0,
    "horizontal_accuracy": 5.0,
    "vertical_accuracy": 3.0,
    "speed": 1.2,
    "course": 45.0,
    "course_accuracy": 10.0
  },
  "risk_score": 0.25,
  "risk_level": "low",
  "battery_level": 0.85,
  "network_status": "wifi"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Data ingested successfully",
  "risk_assessment": {
    "risk_score": 0.25,
    "risk_level": "low",
    "factors": {
      "heart_rate": 0.0,
      "motion": 0.1,
      "location": 0.0
    }
  },
  "alerts": []
}
```

## Risk Scoring API

### POST /score/calculate

**Request Body:**
```json
{
  "officer_id": "uuid",
  "health_data": {
    "heart_rate": 75.0,
    "heart_rate_variability": 42.5,
    "acceleration": {
      "x": 0.1,
      "y": -0.2,
      "z": 9.8
    },
    "activity_type": "walking"
  },
  "location_data": {
    "latitude": 40.7128,
    "longitude": -74.0060,
    "accuracy": 5.0
  },
  "historical_data": {
    "avg_heart_rate": 72.0,
    "recent_risk_events": 0
  }
}
```

**Response:**
```json
{
  "officer_id": "uuid",
  "risk_score": 0.25,
  "risk_level": "low",
  "factors": {
    "heart_rate": 0.0,
    "heart_rate_variability": 0.1,
    "motion": 0.1,
    "fall_detection": 0.0,
    "activity": 0.05,
    "location": 0.0
  },
  "confidence": 0.85,
  "recommendations": [
    "All systems normal - continue monitoring"
  ],
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## WebSocket Events

### Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/live');
```

### Message Types

#### 1. Officer Update
```json
{
  "type": "officer_update",
  "timestamp": "2024-01-01T12:00:00Z",
  "officer_id": "uuid",
  "risk_level": "low",
  "risk_score": 0.25,
  "location": {
    "latitude": 40.7128,
    "longitude": -74.0060,
    "accuracy": 5.0
  },
  "last_seen": "2024-01-01T12:00:00Z"
}
```

#### 2. Risk Event
```json
{
  "type": "risk_event",
  "timestamp": "2024-01-01T12:00:00Z",
  "event_id": "uuid",
  "officer_id": "uuid",
  "event_type": "high_risk",
  "risk_level": "high",
  "description": "Officer John Smith is at high risk",
  "location": {
    "latitude": 40.7128,
    "longitude": -74.0060
  }
}
```

#### 3. System Alert
```json
{
  "type": "system_alert",
  "timestamp": "2024-01-01T12:00:00Z",
  "alert_id": "uuid",
  "alert_type": "officer_down",
  "severity": "critical",
  "title": "Officer Down Alert",
  "message": "Officer John Smith has not responded for 5 minutes",
  "officer_id": "uuid"
}
```

#### 4. Heartbeat
```json
{
  "type": "ping",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## Data Models

### Officer
```typescript
interface Officer {
  id: string;
  badge_number: string;
  name: string;
  department: string;
  phone?: string;
  email?: string;
  is_active: boolean;
  is_on_duty: boolean;
  last_seen: string;
  current_risk_level: "low" | "medium" | "high";
  current_risk_score: number;
  device_id: string;
  app_version?: string;
  created_at: string;
  updated_at: string;
}
```

### Health Data
```typescript
interface HealthData {
  id: string;
  officer_id: string;
  heart_rate?: number;
  heart_rate_variability?: number;
  resting_heart_rate?: number;
  acceleration_x?: number;
  acceleration_y?: number;
  acceleration_z?: number;
  gyroscope_x?: number;
  gyroscope_y?: number;
  gyroscope_z?: number;
  activity_type?: string;
  activity_confidence?: number;
  fall_detected: boolean;
  fall_confidence?: number;
  workout_active: boolean;
  workout_duration?: number;
  raw_sensor_data?: object;
  recorded_at: string;
  created_at: string;
}
```

### Location Data
```typescript
interface LocationData {
  id: string;
  officer_id: string;
  latitude: number;
  longitude: number;
  altitude?: number;
  accuracy?: number;
  horizontal_accuracy?: number;
  vertical_accuracy?: number;
  speed?: number;
  course?: number;
  course_accuracy?: number;
  recorded_at: string;
  created_at: string;
}
```

### Risk Event
```typescript
interface RiskEvent {
  id: string;
  officer_id: string;
  event_type: "high_risk" | "fall_detected" | "sos" | "heart_rate_anomaly" | "motion_anomaly" | "location_anomaly";
  risk_level: "low" | "medium" | "high";
  risk_score: number;
  description?: string;
  metadata?: object;
  latitude?: number;
  longitude?: number;
  is_acknowledged: boolean;
  is_resolved: boolean;
  acknowledged_by?: string;
  resolved_by?: string;
  occurred_at: string;
  acknowledged_at?: string;
  resolved_at?: string;
  created_at: string;
}
```

## Error Responses

### Standard Error Format
```json
{
  "detail": "Error message",
  "status_code": 400,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Common Error Codes
- `400` - Bad Request (invalid data format)
- `401` - Unauthorized (invalid/missing token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (officer/resource not found)
- `422` - Validation Error (invalid field values)
- `500` - Internal Server Error

## Rate Limiting

### Limits
- **Data Ingestion**: 10 requests per second per officer
- **WebSocket Messages**: 100 messages per minute per connection
- **API Calls**: 1000 requests per hour per API key

### Headers
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## Data Validation

### Required Fields
- `officer_id`: Valid UUID format
- `device_id`: Non-empty string
- `timestamp`: ISO 8601 format
- `latitude`: -90 to 90
- `longitude`: -180 to 180

### Optional Fields
- `heart_rate`: 30-250 BPM
- `heart_rate_variability`: 0-200 ms
- `accuracy`: 0-1000 meters
- `risk_score`: 0.0-1.0

## Webhook Events

### Officer Status Change
```json
{
  "event": "officer.status_changed",
  "timestamp": "2024-01-01T12:00:00Z",
  "data": {
    "officer_id": "uuid",
    "old_status": "low",
    "new_status": "high",
    "risk_score": 0.85
  }
}
```

### Emergency Alert
```json
{
  "event": "officer.emergency",
  "timestamp": "2024-01-01T12:00:00Z",
  "data": {
    "officer_id": "uuid",
    "alert_type": "sos",
    "location": {
      "latitude": 40.7128,
      "longitude": -74.0060
    }
  }
}
```

## Mobile App Data Format

### iOS HealthKit Integration
```swift
struct HealthData {
    let heartRate: Double?
    let heartRateVariability: Double?
    let acceleration: CMAcceleration?
    let gyroscope: CMRotationRate?
    let activityType: String?
    let fallDetected: Bool
    let timestamp: Date
}
```

### Watch Connectivity
```swift
struct WatchMessage {
    let type: String
    let data: [String: Any]
    let timestamp: Date
}
```

## Database Schema

### Officers Table
```sql
CREATE TABLE officers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    badge_number VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100),
    is_active BOOLEAN DEFAULT FALSE,
    is_on_duty BOOLEAN DEFAULT FALSE,
    last_seen TIMESTAMP DEFAULT NOW(),
    current_risk_level VARCHAR(20) DEFAULT 'low',
    current_risk_score FLOAT DEFAULT 0.0,
    device_id VARCHAR(100) UNIQUE,
    app_version VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Health Data Table
```sql
CREATE TABLE health_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    officer_id UUID REFERENCES officers(id),
    heart_rate FLOAT,
    heart_rate_variability FLOAT,
    acceleration_x FLOAT,
    acceleration_y FLOAT,
    acceleration_z FLOAT,
    gyroscope_x FLOAT,
    gyroscope_y FLOAT,
    gyroscope_z FLOAT,
    activity_type VARCHAR(50),
    activity_confidence FLOAT,
    fall_detected BOOLEAN DEFAULT FALSE,
    fall_confidence FLOAT,
    workout_active BOOLEAN DEFAULT FALSE,
    workout_duration INTEGER,
    raw_sensor_data JSONB,
    recorded_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Location Data Table
```sql
CREATE TABLE location_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    officer_id UUID REFERENCES officers(id),
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    altitude FLOAT,
    accuracy FLOAT,
    horizontal_accuracy FLOAT,
    vertical_accuracy FLOAT,
    speed FLOAT,
    course FLOAT,
    course_accuracy FLOAT,
    recorded_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Testing

### Sample Test Data
```json
{
  "test_officer": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "badge_number": "PD001",
    "name": "John Smith",
    "department": "Police Department"
  },
  "test_health_data": {
    "heart_rate": 75.0,
    "activity_type": "walking",
    "fall_detected": false
  },
  "test_location_data": {
    "latitude": 40.7128,
    "longitude": -74.0060,
    "accuracy": 5.0
  }
}
```
