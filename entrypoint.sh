#!/bin/bash
set -e

echo "Starting API..."

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
    python3 seed.py
    python3 -c "
import psycopg2
import os
conn = psycopg2.connect(os.environ['DATABASE_URL'])
cur = conn.cursor()
cur.execute(\"UPDATE users SET role='admin' WHERE email IN ('requester@claims.com', 'emilio@claims.com')\")
cur.execute(\"ALTER TABLE cases ADD COLUMN IF NOT EXISTS claimed_amount FLOAT\")
conn.commit()
conn.close()
print('Admin roles set and schema updated.')
"
    echo "Done."
else
    echo "Database already seeded ($USER_COUNT users) — skipping."
fi

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
