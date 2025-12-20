#!/bin/bash

# FareGlitch Quick Start Script
# This script sets up the development environment

set -e  # Exit on error

echo "🚀 FareGlitch Setup Starting..."

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.11"

if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)"; then
    echo "❌ Python 3.11+ required. Found: $python_version"
    exit 1
fi
echo "✅ Python version OK: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt > /dev/null 2>&1
echo "✅ Dependencies installed"

# Copy .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  IMPORTANT: Edit .env and add your API keys!"
else
    echo "✅ .env file already exists"
fi

# Check if Docker is available
if command -v docker &> /dev/null; then
    echo "🐳 Docker detected"
    
    # Ask if user wants to start database
    read -p "Start PostgreSQL with Docker? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗄️  Starting PostgreSQL..."
        docker-compose up -d db
        echo "⏳ Waiting for database to be ready..."
        sleep 10
        echo "✅ Database started"
    fi
else
    echo "⚠️  Docker not found. You'll need to set up PostgreSQL manually."
fi

# Initialize database
echo "🗄️  Initializing database..."
python3 -c "from src.utils.database import init_db; init_db()" 2>/dev/null && echo "✅ Database initialized" || echo "⚠️  Database initialization skipped (configure .env first)"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p cache
echo "✅ Directories created"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Edit .env and add your API keys:"
echo "   nano .env"
echo ""
echo "2. Test the scanner:"
echo "   python -m src.scanner.main --test"
echo ""
echo "3. Start the API server:"
echo "   uvicorn src.api.main:app --reload"
echo ""
echo "4. Run tests:"
echo "   pytest tests/ -v"
echo ""
echo "📚 Documentation:"
echo "   - Setup Guide: docs/SETUP_GUIDE.md"
echo "   - HubSpot Config: docs/HUBSPOT_SETUP.md"
echo "   - API Docs: http://localhost:8000/docs (after starting server)"
echo ""
echo "🆘 Need help? Check the README.md"
echo ""
