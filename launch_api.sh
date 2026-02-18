#!/bin/bash
# Complete Setup and Launch Script for FareGlitch

echo "🚀 FareGlitch Setup - Production Ready"
echo "========================================="
echo ""

# Step 1: Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Step 2: Initialize database
echo "🗄️ Initializing database..."
python -c "from src.utils.database import init_db; init_db()"

# Step 3: Start the API server
echo "🌐 Starting API server..."
echo "API will be available at http://localhost:8000"
echo ""
echo "📝 API Endpoints:"
echo "  - GET  /deals/active - Get active deals (respects member status)"
echo "  - POST /auth/login - Login and get JWT token"
echo "  - GET  /auth/me - Get current user info"
echo "  - GET  /docs - API documentation"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
