# Claims Platform

A full-stack case management and workflow automation API built with Python, FastAPI, and PostgreSQL. Inspired by a real corporate automation I built that reduced claim resolution time from 2–3 weeks to 2 days.

## Live API

http://54.172.217.112:8000/docs

## What it does

- Users can create claims and operational requests
- Cases move through a structured workflow with role-based access
- Every status change is logged with a full audit trail
- SLA deadlines are tracked automatically
- Overdue cases are escalated by a background job

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI |
| Database | PostgreSQL |
| Auth | JWT tokens |
| Containers | Docker, Docker Compose |
| Cloud | AWS EC2 |

## API Endpoints

### Auth
- `POST /auth/register` — create account
- `POST /auth/login` — get JWT token

### Cases
- `POST /cases/` — create a case
- `GET /cases/` — list all cases
- `GET /cases/{id}` — get case detail
- `POST /cases/{id}/transition` — move case to next status

### Comments
- `POST /cases/{id}/comments` — add comment
- `GET /cases/{id}/comments` — list comments

### Analytics
- `GET /analytics/summary` — case counts by status
- `GET /analytics/sla-breaches` — overdue cases

## Workflow
open → in_review → pending_approval → approved → resolved
↘ rejected → open
open/in_review → escalated → in_review
## Running locally

```bash
git clone https://github.com/emiliognatividad/claims-platform.git
cd claims-platform
docker compose up --build
```

API will be available at `http://localhost:8000/docs`

## Background

This project is a technical rebuild of a workflow automation I built at a corporate environment using Microsoft Power Automate, Teams, and Excel. The original system cut claim resolution time from 2–3 weeks to approximately 2 days across 10+ stakeholders. This version rebuilds that logic as a proper software engineering project.