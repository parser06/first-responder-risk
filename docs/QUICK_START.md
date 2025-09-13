# Quick Start Guide - First Responder Risk Monitoring System

## Prerequisites

Before starting, ensure you have the following installed:

- **Docker & Docker Compose** - For infrastructure services
- **Python 3.9+** - For the backend API
- **Node.js 18+** - For the web dashboard
- **Xcode 15+** - For iOS/watchOS development (macOS only)

## 🚀 Quick Setup (5 minutes)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd first-responder-risk
```

### 2. Start Infrastructure
```bash
make dev-up
```
This starts PostgreSQL, Redis, and pgAdmin in Docker containers.

### 3. Install Dependencies
```bash
make install-server  # Python dependencies
make install-web     # Node.js dependencies
```

### 4. Start All Services
```bash
make start-all
```

### 5. Access the Applications
- **Web Dashboard**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **pgAdmin**: http://localhost:5050 (admin@firstresponder.com / admin)

## 📱 Mobile App Setup

### iOS App (Xcode Required)
1. Open `mobile/FirstResponder.xcworkspace` in Xcode
2. Select your development team
3. Build and run on simulator or device
4. Grant location and health permissions when prompted

### Apple Watch App
1. The watch app is included in the iOS workspace
2. Build and run on paired Apple Watch
3. Grant health permissions for heart rate monitoring

## 🧪 Testing the System

### 1. Test Data Ingestion
```bash
curl -X POST http://localhost:8000/api/v1/ingest/data \
  -H "Content-Type: application/json" \
  -d '{
    "officer_id": "550e8400-e29b-41d4-a716-446655440000",
    "device_id": "test-device-001",
    "timestamp": "2024-01-01T12:00:00Z",
    "sensor_data": {
      "heart_rate": 75.0,
      "activity_type": "walking",
      "fall_detected": false
    },
    "location_data": {
      "latitude": 40.7128,
      "longitude": -74.0060,
      "accuracy": 5.0
    }
  }'
```

### 2. View Officers
```bash
curl http://localhost:8000/api/v1/ingest/officers
```

### 3. Test WebSocket Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/live');
ws.onopen = () => console.log('Connected');
ws.onmessage = (event) => console.log('Message:', JSON.parse(event.data));
```

## 🔧 Development Commands

### Backend Development
```bash
cd server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Web Dashboard Development
```bash
cd web
npm run dev
```

### Database Operations
```bash
make db-migrate    # Run migrations
make db-reset      # Reset database
make logs          # View service logs
```

### Clean Up
```bash
make clean         # Remove all containers and volumes
make dev-down      # Stop services only
```

## 📊 Sample Data

The system comes with sample officer data for testing:

- **Officer 1**: John Smith (PD001) - Police Department
- **Officer 2**: Sarah Johnson (FD002) - Fire Department  
- **Officer 3**: Mike Davis (EMT003) - Emergency Medical

## 🎯 Key Features to Test

### 1. Real-time Monitoring
- Open the web dashboard
- Start the iOS app and begin monitoring
- Watch real-time updates on the map

### 2. Risk Assessment
- Simulate different heart rates and activities
- Observe risk level changes
- Test fall detection scenarios

### 3. Emergency Response
- Press the SOS button in the iOS app
- Verify alerts appear in the dashboard
- Check WebSocket notifications

### 4. Data Persistence
- View historical data in pgAdmin
- Check officer status over time
- Verify data accuracy and completeness

## 🐛 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Kill processes using ports 3000, 8000, 5432, 6379
lsof -ti:3000,8000,5432,6379 | xargs kill -9
```

#### 2. Docker Issues
```bash
# Reset Docker
docker system prune -a
make clean
make dev-up
```

#### 3. Database Connection Issues
```bash
# Check if PostgreSQL is running
docker ps | grep postgres
# Check logs
make logs
```

#### 4. Mobile App Issues
- Ensure Xcode is up to date
- Check device/simulator is properly connected
- Verify provisioning profiles

### Logs and Debugging

#### Backend Logs
```bash
cd server
tail -f logs/app.log
```

#### Web Dashboard Logs
```bash
cd web
npm run dev  # Check console output
```

#### Infrastructure Logs
```bash
make logs
```

## 📚 Next Steps

1. **Read the Architecture**: See `docs/ARCHITECTURE.md`
2. **API Reference**: Visit http://localhost:8000/docs
3. **Data Contracts**: See `docs/DATA_CONTRACTS.md`
4. **Customize**: Modify risk thresholds and algorithms
5. **Deploy**: Follow production deployment guide

## 🆘 Getting Help

- **Documentation**: Check the `docs/` folder
- **API Docs**: http://localhost:8000/docs
- **Issues**: Create an issue in the repository
- **Discussions**: Use GitHub Discussions for questions

## 🎉 Success!

If you can see the web dashboard, send test data, and view officer locations on the map, you've successfully set up the First Responder Risk Monitoring System!

The system is now ready for:
- Adding more officers
- Customizing risk algorithms
- Integrating with real devices
- Deploying to production
