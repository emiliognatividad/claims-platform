#!/bin/bash
set -e

echo "Starting API..."

echo "Creating tables..."
python3 -c "
from app.database import engine, Base
from app.models import user, case, comment, case_history
Base.metadata.create_all(bind=engine)
print('Tables ready.')
"

USER_COUNT=$(python3 -c "
import psycopg2
import os
try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM users')
    print(cur.fetchone()[0])
    conn.close()
except:
    print(0)
")

if [ "$USER_COUNT" = "0" ]; then
    echo "Database empty — seeding..."
    python3 seed_direct.py
    echo "Done."
else
    echo "Database already seeded ($USER_COUNT users) — skipping."
fi

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
