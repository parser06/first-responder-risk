# Alternative Setup Without Docker

Since Docker is having authentication issues, here's how to set up the system using local installations:

## Option 1: Install PostgreSQL and Redis Locally

### macOS (using Homebrew)
```bash
# Install PostgreSQL
brew install postgresql@15
brew services start postgresql@15

# Install Redis
brew install redis
brew services start redis

# Create database
createdb first_responder_risk
```

### Ubuntu/Debian
```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib postgresql-15-postgis

# Install Redis
sudo apt install redis-server

# Start services
sudo systemctl start postgresql
sudo systemctl start redis

# Create database
sudo -u postgres createdb first_responder_risk
```

## Option 2: Use SQLite (Simplest)

Update the server configuration to use SQLite instead:

1. Update `server/app/config.py`:
```python
DATABASE_URL = "sqlite:///./first_responder_risk.db"
```

2. Update `server/requirements.txt`:
```
# Replace psycopg2-binary with:
sqlite3  # Built into Python
```

3. Remove Redis dependency and use in-memory caching

## Option 3: Fix Docker Authentication

1. **Check Docker Desktop Settings**:
   - Open Docker Desktop
   - Go to Settings → Docker Engine
   - Look for any authentication configuration
   - Remove any Docker Hub login credentials

2. **Reset Docker Desktop**:
   - Quit Docker Desktop
   - Delete `~/Library/Group Containers/group.com.docker`
   - Restart Docker Desktop

3. **Try logging out and back in**:
   ```bash
   docker logout
   docker login
   ```

## Quick Start with Local PostgreSQL

1. Install PostgreSQL locally (see above)
2. Start the backend:
   ```bash
   cd server
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```
3. Start the web dashboard:
   ```bash
   cd web
   npm install
   npm run dev
   ```

The system will work the same way, just without Docker containers.
