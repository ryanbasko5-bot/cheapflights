#!/bin/bash

# Database initialization and migration script

set -e

echo "🗄️  Database Setup"

# Load environment
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check if database URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL not set in .env"
    exit 1
fi

echo "📊 Database URL: ${DATABASE_URL%%@*}@***"

# Initialize database schema
echo "🔨 Creating database schema..."
python3 -c "
from src.utils.database import init_db
from src.models.database import Base, Deal, DealUnlock, PriceHistory, ScanLog
print('📋 Tables to create:')
for table in Base.metadata.sorted_tables:
    print(f'  - {table.name}')
init_db()
print('✅ Database schema created')
"

# Optional: Load sample data
read -p "Load sample data for testing? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📦 Loading sample data..."
    python3 -c "
from src.models.database import Deal, PriceHistory, DealStatus
from src.utils.database import get_db_session
from datetime import datetime, timedelta

db = next(get_db_session())

# Sample price history
print('Adding sample price history...')
history = [
    PriceHistory(origin='JFK', destination='NRT', price=2000, currency='USD', data_source='manual'),
    PriceHistory(origin='LAX', destination='NRT', price=1800, currency='USD', data_source='manual'),
    PriceHistory(origin='JFK', destination='LHR', price=1500, currency='USD', data_source='manual'),
]
for h in history:
    db.add(h)

# Sample deal
print('Adding sample deal...')
deal = Deal(
    deal_number='DEAL#001',
    origin='JFK',
    destination='NRT',
    route_description='New York to Tokyo',
    normal_price=2000.0,
    mistake_price=450.0,
    savings_amount=1550.0,
    savings_percentage=0.775,
    currency='USD',
    cabin_class='business',
    airline='ANA',
    status=DealStatus.VALIDATED,
    teaser_headline='Business Class Glitch: NYC to Tokyo',
    teaser_description='Fly ANA Business Class for 77% off',
    unlock_fee=7.0,
    expires_at=datetime.now() + timedelta(hours=48)
)
db.add(deal)

db.commit()
print('✅ Sample data loaded')
"
fi

echo ""
echo "✅ Database setup complete!"
