from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.database import get_db
from app.models.comment import Comment
from app.models.case import Case
from app.models.user import User

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

@router.post("/{case_id}/comments")
def add_comment(
    case_id: UUID,
    body: dict,
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
        body=body["body"]
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return {
        "id": str(comment.id),
        "case_id": str(comment.case_id),
        "author_id": str(comment.author_id),
        "author_name": user.full_name,
        "body": comment.body,
        "created_at": comment.created_at.isoformat()
    }

@router.get("/{case_id}/comments")
def list_comments(
    case_id: UUID,
    token: str,
    db: Session = Depends(get_db)
):
    get_current_user(token, db)
    comments = db.query(Comment).filter(Comment.case_id == case_id).all()
    result = []
    for c in comments:
        author = db.query(User).filter(User.id == c.author_id).first()
        result.append({
            "id": str(c.id),
            "case_id": str(c.case_id),
            "author_id": str(c.author_id),
            "author_name": author.full_name if author else "Unknown",
            "body": c.body,
            "created_at": c.created_at.isoformat()
        })
    return result
    