from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import User
from app.schemas import MessageResponse


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/deactivate", response_model=MessageResponse)
def deactivate_account(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    current_user.is_active = False
    db.commit()
    return {"message": "Account deactivated"}
