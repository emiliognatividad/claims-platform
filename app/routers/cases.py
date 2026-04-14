from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime, timedelta
from typing import List

from app.database import get_db
from app.models.case import Case
from app.models.user import User
from app.schemas.case import CaseCreate, CaseResponse, CaseUpdate

router = APIRouter(prefix="/cases", tags=["cases"])

def get_current_user(token: str, db: Session) -> User:
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

@router.post("/", response_model=CaseResponse)
def create_case(
    body: CaseCreate,
    token: str,
    db: Session = Depends(get_db)
):
    user = get_current_user(token, db)
    case = Case(
        title=body.title,
        description=body.description,
        priority=body.priority,
        created_by=user.id,
        sla_deadline=datetime.utcnow() + timedelta(days=5)
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    return case

@router.get("/", response_model=List[CaseResponse])
def list_cases(
    token: str,
    db: Session = Depends(get_db)
):
    get_current_user(token, db)
    cases = db.query(Case).all()
    return cases

@router.get("/{case_id}", response_model=CaseResponse)
def get_case(
    case_id: UUID,
    token: str,
    db: Session = Depends(get_db)
):
    get_current_user(token, db)
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case
    