#!/bin/bash

echo "🚀 FareGlitch MVP Setup"
echo "======================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ No .env file found!"
    echo "   Creating one now from .env.example..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your Sinch credentials!"
    echo "   1. Go to: https://dashboard.sinch.com/signup"
    echo "   2. Get your Service Plan ID and API Token"
    echo "   3. Buy a phone number"
    echo "   4. Edit .env and fill in SINCH_* variables"
    echo ""
    exit 1
fi

echo "✅ Found .env file"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment exists"
fi

echo ""
echo "📦 Activating virtual environment..."
source venv/bin/activate

echo ""
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "🔍 Testing Amadeus API..."
python3 -c "
from amadeus import Client
import os
from dotenv import load_dotenv

load_dotenv()

try:
    amadeus = Client(
        client_id=os.getenv('AMADEUS_API_KEY'),
        client_secret=os.getenv('AMADEUS_API_SECRET')
    )
    print('✅ Amadeus API working!')
except Exception as e:
    print(f'❌ Amadeus API failed: {e}')
    exit(1)
"

echo ""
echo "📱 Testing Sinch SMS..."
python3 -c "
from clx.xms import Client
import os
from dotenv import load_dotenv

load_dotenv()

service_plan_id = os.getenv('SINCH_SERVICE_PLAN_ID')
api_token = os.getenv('SINCH_API_TOKEN')

if not service_plan_id or service_plan_id == 'your_service_plan_id_here':
    print('⚠️  Sinch not configured yet')
    print('   1. Go to: https://dashboard.sinch.com/signup')
    print('   2. Get credentials and update .env file')
    print('   3. Run this script again')
    exit(0)

try:
    sinch = Client(
        service_plan_id=service_plan_id,
        token=api_token
    )
    print('✅ Sinch SMS configured!')
except Exception as e:
    print(f'❌ Sinch failed: {e}')
    print('   Check your credentials in .env')
    exit(1)
"

echo ""
echo "="
echo "🎉 Setup Complete!"
echo "="
echo ""
echo "Next steps:"
echo "1. Make sure Sinch is configured in .env"
echo "2. Run: python3 test_mvp.py"
echo "3. Check your phone for SMS!"
echo ""
