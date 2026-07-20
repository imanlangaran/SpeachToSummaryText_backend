#!/bin/bash
set -e

echo "⏳ Waiting for MySQL to be ready..."

# Build DATABASE_URL from individual vars if not already set
if [ -z "$DATABASE_URL" ]; then
    DB_HOST="${DB_HOST:-db}"
    DB_PORT="${DB_PORT:-3306}"
    DB_USER="${DB_USER:-root}"
    DB_PASSWORD="${DB_PASSWORD:-}"
    DB_NAME="${DB_NAME:-speech_to_summary}"
    if [ -n "$DB_PASSWORD" ]; then
        DATABASE_URL="mysql+pymysql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}"
    else
        DATABASE_URL="mysql+pymysql://${DB_USER}@${DB_HOST}:${DB_PORT}/${DB_NAME}"
    fi
    export DATABASE_URL
    echo "📋 DATABASE_URL configured from individual env vars"
fi

# Retry loop — wait for MySQL to accept connections
for i in $(seq 1 30); do
    if python3 -c "
import pymysql
try:
    pymysql.connect(
        host='${DB_HOST:-db}',
        port=${DB_PORT:-3306},
        user='${DB_USER:-root}',
        password='${DB_PASSWORD:-}',
        connect_timeout=2,
    )
    print('OK')
except Exception as e:
    print(f'waiting... {e}')
" 2>/dev/null | grep -q OK; then
        echo "✅ MySQL is ready!"
        break
    fi
    echo "  Attempt $i/30 — MySQL not ready yet..."
    sleep 2
done

# Create database if it doesn't exist
python3 -c "
import pymysql
conn = pymysql.connect(
    host='${DB_HOST:-db}', port=${DB_PORT:-3306},
    user='${DB_USER:-root}', password='${DB_PASSWORD:-}',
)
cursor = conn.cursor()
db_name = '${DB_NAME:-speech_to_summary}'
cursor.execute(f'CREATE DATABASE IF NOT EXISTS \`{db_name}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
cursor.close()
conn.close()
print(f'✅ Database \`{db_name}\` ready')
"

# Run database migrations
echo "📦 Running Alembic migrations..."
alembic upgrade head
echo "✅ Migrations applied!"

# Start the application
echo "🚀 Starting Voice Summary API..."
exec python3 -m uvicorn app.main:app \
    --host 0.0.0.0 \
    --port "${PORT:-8000}" \
    ${UVICORN_EXTRA_ARGS:-}
