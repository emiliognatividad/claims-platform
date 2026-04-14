from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.case import Case
from app.models.user import User

router = APIRouter(prefix="/analytics", tags=["analytics"])

def get_current_user(token: str, db: Session):
    from jose import jwt, JWTError
    from app.config import settings
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/summary")
def get_summary(token: str, db: Session = Depends(get_db)):
    get_current_user(token, db)

    total = db.query(Case).count()
    open_cases = db.query(Case).filter(Case.status == "open").count()
    in_review = db.query(Case).filter(Case.status == "in_review").count()
    escalated = db.query(Case).filter(Case.status == "escalated").count()
    resolved = db.query(Case).filter(Case.status == "resolved").count()
    pending = db.query(Case).filter(Case.status == "pending_approval").count()

    return {
        "total": total,
        "open": open_cases,
        "in_review": in_review,
        "pending_approval": pending,
        "escalated": escalated,
        "resolved": resolved,
    }

@router.get("/sla-breaches")
def get_sla_breaches(token: str, db: Session = Depends(get_db)):
    from datetime import datetime
    get_current_user(token, db)

    breached = db.query(Case).filter(
        Case.sla_deadline < datetime.utcnow(),
        Case.status.notin_(["resolved", "rejected"])
    ).all()

    return {
        "count": len(breached),
        "cases": [
            {
                "id": str(c.id),
                "title": c.title,
                "status": c.status,
                "sla_deadline": c.sla_deadline
            }
            for c in breached
        ]
    }
    