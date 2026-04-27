# Claims Management Platform

Full-stack internal workflow system for logistics claims. Built from a real operational problem where claims lived in email chains with no visibility or SLAs.

## Live Demo

- Frontend: http://54.172.217.112
- API: http://54.172.217.112:8000
- API Docs: http://54.172.217.112:8000/docs

**Demo credentials**
| Role | Email | Password |
|------|-------|----------|
| Admin | requester@claims.com | 123456 |
| Agent | agent1@claims.com | 123456 |
| Manager | manager@claims.com | 123456 |

## Features

- Role-based access control (admin, agent, manager, requester)
- Workflow state machine: open, in_review, pending_approval, approved/rejected, resolved
- SLA tracking with color indicators
- Full audit trail on every state transition
- Analytics dashboard with charts by status and volume
- CSV export
- Credit note generation on resolved cases
- Dark mode, mobile responsive

## Stack

**Backend:** Python, FastAPI, PostgreSQL, SQLAlchemy, JWT, bcrypt, Docker, AWS EC2, nginx

**Frontend:** React, Recharts

## Running locally

**Backend**
```bash
cd claims-platform
docker compose up -d
```

API runs at http://localhost:8000. Database auto-seeds on startup with 5 users and 30 sample cases across 7 industries and 21 clients.

**Frontend**
```bash
cd claims-frontend
npm install
REACT_APP_API_URL=http://localhost:8000 npm start
```

## Structure

```
claims-platform/
├── app/
│   ├── main.py
│   ├── models/        # user, case, comment, case_history
│   └── routers/       # auth, cases, comments, analytics
├── seed_direct.py
├── entrypoint.sh
├── Dockerfile
└── docker-compose.yml
```
