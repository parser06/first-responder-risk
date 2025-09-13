# First Responder Risk Monitoring System - Development Makefile

.PHONY: help dev-up dev-down install-server install-web start-server start-web start-all clean

# Default target
help:
	@echo "First Responder Risk Monitoring System"
	@echo "======================================"
	@echo ""
	@echo "Available commands:"
	@echo "  dev-up          Start all services (PostgreSQL, Redis, pgAdmin)"
	@echo "  dev-down        Stop all services"
	@echo "  install-server  Install Python dependencies"
	@echo "  install-web     Install Node.js dependencies"
	@echo "  start-server    Start FastAPI backend server"
	@echo "  start-web       Start Next.js web dashboard"
	@echo "  start-all       Start both server and web"
	@echo "  clean           Clean up containers and volumes"
	@echo "  logs            View logs from all services"
	@echo "  test            Run tests"

# Start development infrastructure
dev-up:
	@echo "Starting development infrastructure..."
	cd infra && docker-compose up -d
	@echo "Waiting for services to be ready..."
	@sleep 10
	@echo "Infrastructure started successfully!"
	@echo "PostgreSQL: localhost:5432"
	@echo "Redis: localhost:6379"
	@echo "pgAdmin: http://localhost:5050 (admin@firstresponder.com / admin)"

# Stop development infrastructure
dev-down:
	@echo "Stopping development infrastructure..."
	cd infra && docker-compose down

# Install Python dependencies
install-server:
	@echo "Installing Python dependencies..."
	cd server && pip install -r requirements.txt

# Install Node.js dependencies
install-web:
	@echo "Installing Node.js dependencies..."
	cd web && npm install

# Start FastAPI server
start-server:
	@echo "Starting FastAPI server..."
	cd server && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start Next.js web dashboard
start-web:
	@echo "Starting Next.js web dashboard..."
	cd web && npm run dev

# Start both server and web (in background)
start-all: dev-up
	@echo "Starting all services..."
	@echo "Starting FastAPI server in background..."
	cd server && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
	@echo "Starting Next.js web dashboard in background..."
	cd web && npm run dev &
	@echo "All services started!"
	@echo "API: http://localhost:8000"
	@echo "Web Dashboard: http://localhost:3000"

# Clean up everything
clean:
	@echo "Cleaning up containers and volumes..."
	cd infra && docker-compose down -v --remove-orphans
	docker system prune -f

# View logs
logs:
	cd infra && docker-compose logs -f

# Run tests
test:
	@echo "Running tests..."
	cd server && python -m pytest tests/ -v
	cd web && npm test

# Database operations
db-migrate:
	@echo "Running database migrations..."
	cd server && alembic upgrade head

db-reset:
	@echo "Resetting database..."
	cd infra && docker-compose down -v
	cd infra && docker-compose up -d
	@sleep 10
	cd server && alembic upgrade head

# Development setup
setup: dev-up install-server install-web
	@echo "Development environment setup complete!"
	@echo "Run 'make start-all' to start all services"

# Production build
build-web:
	@echo "Building web dashboard for production..."
	cd web && npm run build

# Health check
health:
	@echo "Checking service health..."
	@curl -s http://localhost:8000/health || echo "Server not running"
	@curl -s http://localhost:3000 > /dev/null && echo "Web dashboard running" || echo "Web dashboard not running"
