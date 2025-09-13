#!/bin/bash

# First Responder Risk Monitoring - Development Setup Script

set -e

echo "🚀 Starting First Responder Risk Monitoring Development Environment"
echo "=================================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if required tools are installed
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 is required but not installed."; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js is required but not installed."; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "❌ npm is required but not installed."; exit 1; }

echo "✅ Prerequisites check passed"

# Start infrastructure
echo "🐳 Starting infrastructure services..."
cd infra
docker-compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 15

# Check if services are running
if ! docker-compose ps | grep -q "Up"; then
    echo "❌ Failed to start infrastructure services"
    docker-compose logs
    exit 1
fi

echo "✅ Infrastructure services started"

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
cd ../server
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt

echo "✅ Python dependencies installed"

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
cd ../web
npm install

echo "✅ Node.js dependencies installed"

# Create environment files if they don't exist
echo "📝 Setting up environment files..."

if [ ! -f "../server/.env" ]; then
    cp ../server/.env.example ../server/.env
    echo "✅ Created server/.env from example"
fi

if [ ! -f "../web/.env.local" ]; then
    cp ../web/.env.local.example ../web/.env.local
    echo "✅ Created web/.env.local from example"
fi

echo ""
echo "🎉 Development environment setup complete!"
echo ""
echo "To start the services:"
echo "  make start-all"
echo ""
echo "Or start them individually:"
echo "  make start-server  # FastAPI backend on http://localhost:8000"
echo "  make start-web     # Next.js dashboard on http://localhost:3000"
echo ""
echo "Infrastructure:"
echo "  PostgreSQL: localhost:5432"
echo "  Redis: localhost:6379"
echo "  pgAdmin: http://localhost:5050 (admin@firstresponder.com / admin)"
echo ""
echo "Happy coding! 🚀"
