# First Responder Risk Monitoring System

A comprehensive real-time monitoring system for first responders (police officers, firefighters, EMTs) that uses Apple Watch and iPhone to collect vital signs, motion data, and location information to assess risk levels and provide emergency alerts.

## 🎯 Project Overview

This system monitors first responders in real-time using:
- **Apple Watch**: Heart rate, HRV, motion sensors, fall detection, activity state
- **iPhone**: GPS location, network connectivity, data buffering, user interface
- **Cloud Backend**: Real-time data processing, risk scoring, WebSocket updates
- **Command Dashboard**: Live map view of all officers with risk levels and alerts

## 🏗️ Architecture

### Edge (Officer)
- **watchOS App**: Primary data collection from health sensors and motion
- **iOS App**: GPS tracking, network uplink, offline data buffering
- **Risk Engine**: Real-time risk scoring based on vital signs and motion patterns

### Cloud
- **FastAPI Backend**: Data ingestion, WebSocket live updates, risk verification
- **PostgreSQL + PostGIS**: Officer locations, historical data, geospatial queries
- **Redis**: Real-time data caching and session management

### Command Dashboard
- **Next.js Web App**: Live map with officer positions, risk levels, and alerts
- **Real-time Updates**: WebSocket integration for live officer status

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.9+
- PostgreSQL with PostGIS
- Redis
- Xcode 15+ (for mobile development)

### Development Setup

1. **Start Infrastructure**
   ```bash
   make dev-up
   ```

2. **Start Backend Server (Flask + SQLite, Demo)**
   ```bash
   cd server
   pip install -r requirements.txt
   python app.py
   # or: FLASK_APP=app.py flask run -p 8000 -h 0.0.0.0
   ```

   Optional: seed demo data
   ```bash
   curl -X POST http://localhost:8000/api/dev/reset
   curl -X POST http://localhost:8000/api/dev/seed
   ```

3. **Start Web Dashboard**
   ```bash
   cd web
   npm install
   npm run dev
   ```

4. **Open Mobile App in Xcode**
   ```bash
   cd mobile
   open FirstResponder.xcworkspace
   ```

## 📁 Project Structure

```
first-responder-risk/
├── server/          # Flask demo backend (SQLite, server/app.py)
├── web/            # Next.js dashboard with map
├── mobile/         # iOS + watchOS apps
├── ml/             # Risk scoring models and training
├── infra/          # Docker and deployment configs
├── docs/           # Architecture and API documentation
└── scripts/        # Development and deployment scripts
```

## 🔧 Key Features

- Demo-focused: iOS/watch app can POST officer snapshots to `/api/officers/upsert`.
- Dashboard polls `/api/officers` every 3s and displays current officer status on a map and list.
- SQLite database file (`server_demo.db`) created automatically on first run.

## 📊 Risk Assessment Factors

- **Heart Rate Variability**: Stress and fatigue indicators
- **Motion Patterns**: Unusual movement or lack thereof
- **Fall Events**: Sudden impacts or loss of consciousness
- **Activity State**: Workout intensity and duration
- **Location Context**: Known high-risk areas

## 🔒 Privacy & Security

- All health data is encrypted in transit and at rest
- Officers must explicitly consent to monitoring
- Data retention policies for compliance
- Secure device enrollment and authentication

## 🚨 Emergency Features

- **SOS Button**: Manual emergency trigger
- **Automatic Alerts**: System-triggered based on risk scores
- **Haptic Feedback**: Watch vibrations for immediate attention
- **Location Sharing**: Real-time GPS coordinates to command center

## 📱 Mobile Apps

### iOS App Features
- Officer enrollment and consent management
- Real-time location tracking
- Watch connectivity and data synchronization
- Offline data buffering
- Emergency contact interface

### watchOS App Features
- Health data collection during workouts
- Motion sensor monitoring
- Haptic alert system
- Quick SOS functionality
- Battery optimization

## 🌐 Web Dashboard

- **Live Map**: Real-time officer positions with risk indicators
- **Officer List**: Detailed status of all active officers
- **Alert Panel**: Emergency notifications and response actions
- **Historical Data**: Past incidents and risk patterns
- **Filtering**: Search by risk level, location, or officer

## 🤝 Contributing

This is a hackathon project. See `docs/ARCHITECTURE.md` for technical details and `docs/DATA_CONTRACTS.md` for API specifications.

## 📄 License

MIT License - See LICENSE file for details
