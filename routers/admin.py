
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from authentication import get_db, require_role
from models import User
from schemas import AdminUserCreate, UserResponse
from enums import UserRole
from utils import get_password_hash

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def create_user(
    user_data: AdminUserCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(
        require_role(UserRole.ADMIN)
    )
):
    # Only allow creation of support and manager accounts
    if user_data.role not in (
        UserRole.SUPPORT,
        UserRole.MANAGER
    ):
        raise HTTPException(
            status_code=400,
            detail="Only support and manager accounts can be created here"
        )

    # Check whether the email is already registered
    existing_user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Hash the password before storing it
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        role=user_data.role,
        is_active=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
