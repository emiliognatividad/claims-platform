from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.database import get_db
from app.models.comment import Comment
from app.models.case import Case
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentResponse

router = APIRouter(prefix="/cases", tags=["comments"])

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

@router.post("/{case_id}/comments", response_model=CommentResponse)
def add_comment(
    case_id: UUID,
    body: CommentCreate,
    token: str,
    db: Session = Depends(get_db)
):
    user = get_current_user(token, db)
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    comment = Comment(
        case_id=case_id,
        author_id=user.id,
        body=body.body
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

@router.get("/{case_id}/comments", response_model=List[CommentResponse])
def list_comments(
    case_id: UUID,
    token: str,
    db: Session = Depends(get_db)
):
    get_current_user(token, db)
    comments = db.query(Comment).filter(Comment.case_id == case_id).all()
    return comments