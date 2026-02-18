#!/usr/bin/env bash
# Production start script for FareGlitch
# Used by Railway / Docker in production deployments
set -euo pipefail

echo "🚀 FareGlitch Production Startup"
echo "================================="

# 1. Run database migrations
echo "📦 Running database migrations..."
python -m alembic upgrade head
echo "✅ Migrations complete"

# 2. Optional: validate environment
echo "🔍 Checking environment..."
python check_env.py || true   # warn but don't block startup

# 3. Start the API server
PORT="${PORT:-8000}"
WORKERS="${WEB_CONCURRENCY:-2}"
echo "🌐 Starting uvicorn on port $PORT with $WORKERS workers..."

exec uvicorn src.api.main:app \
    --host 0.0.0.0 \
    --port "$PORT" \
    --workers "$WORKERS" \
    --log-level info \
    --access-log \
    --proxy-headers \
    --forwarded-allow-ips='*'
