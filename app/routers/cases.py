from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime, timedelta
from typing import List, Optional

from app.database import get_db
from app.models.case import Case
from app.models.user import User
from app.models.case_history import CaseHistory
from app.schemas.case import CaseCreate, CaseResponse, CaseUpdate

router = APIRouter(prefix="/cases", tags=["cases"])

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

TRANSITIONS = {
    "open":             ["in_review", "escalated"],
    "in_review":        ["pending_approval", "escalated"],
    "escalated":        ["in_review"],
    "pending_approval": ["approved", "rejected"],
    "approved":         ["resolved"],
    "rejected":         ["open"],
}

@router.post("/", response_model=CaseResponse)
def create_case(body: CaseCreate, token: str, db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    case = Case(
        title=body.title,
        description=body.description,
        priority=body.priority,
        claimed_amount=body.claimed_amount,
        created_by=user.id,
        sla_deadline=datetime.utcnow() + timedelta(days=5)
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    return case

@router.get("/", response_model=List[CaseResponse])
def list_cases(token: str, db: Session = Depends(get_db)):
    get_current_user(token, db)
    cases = db.query(Case).all()
    return cases

@router.get("/{case_id}", response_model=CaseResponse)
def get_case(case_id: UUID, token: str, db: Session = Depends(get_db)):
    get_current_user(token, db)
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

@router.post("/{case_id}/transition", response_model=CaseResponse)
def transition_case(
    case_id: UUID,
    to_status: str,
    token: str,
    note: Optional[str] = None,
    db: Session = Depends(get_db)
):
    user = get_current_user(token, db)
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    allowed = TRANSITIONS.get(case.status, [])
    if to_status not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot move from {case.status} to {to_status}"
        )

    old_status = case.status
    case.status = to_status
    if to_status == "resolved":
        case.resolved_at = datetime.utcnow()

    history = CaseHistory(
        case_id=case.id,
        changed_by=user.id,
        from_status=old_status,
        to_status=to_status,
        note=note
    )
    db.add(history)
    db.commit()
    db.refresh(case)
    return case

@router.get("/{case_id}/history")
def get_history(case_id: UUID, token: str, db: Session = Depends(get_db)):
    get_current_user(token, db)
    history = db.query(CaseHistory).filter(
        CaseHistory.case_id == case_id
    ).order_by(CaseHistory.changed_at.asc()).all()
    return [{
        "id": str(h.id),
        "from_status": h.from_status,
        "to_status": h.to_status,
        "note": h.note,
        "changed_at": h.changed_at.isoformat()
    } for h in history]
    
@router.get("/users/list")
def list_users(token: str, db: Session = Depends(get_db)):
    get_current_user(token, db)
    users = db.query(User).all()
    return [{"id": str(u.id), "full_name": u.full_name, "role": u.role} for u in users]

@router.patch("/{case_id}/assign")
def assign_case(case_id: UUID, token: str, assigned_to: str, db: Session = Depends(get_db)):
    get_current_user(token, db)
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    case.assigned_to = assigned_to
    db.commit()
    db.refresh(case)
    return {"assigned_to": str(case.assigned_to)}
    