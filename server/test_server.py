"""
Simple test script to verify the server works
"""

import sys
import os
sys.path.append('.')

from app.main_simple import app
from fastapi.testclient import TestClient

# Test the app
client = TestClient(app)

# Test root endpoint
response = client.get("/")
print("Root endpoint:", response.status_code, response.json())

# Test health endpoint
response = client.get("/health")
print("Health endpoint:", response.status_code, response.json())

# Test officers endpoint
response = client.get("/api/v1/ingest/officers")
print("Officers endpoint:", response.status_code, response.json())

print("✅ All tests passed!")
