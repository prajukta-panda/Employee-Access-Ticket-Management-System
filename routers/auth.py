from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from authentication import get_db, authenticate_user
from models import User
from schemas import UserCreate, UserResponse, Token, LoginRequest
from utils import get_password_hash, create_access_token
from enums import UserRole
from fastapi import Depends
from authentication import get_current_user
from authentication import require_role

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/register",response_model=UserResponse,status_code=status.HTTP_201_CREATED
)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
): 
    # 1. Check whether email already exists
    existing_user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # 2. Hash the password
    hashed_password = get_password_hash(user_data.password)

    # 3. Create SQLAlchemy User object
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hashed_password,
        role=UserRole.EMPLOYEE
    )

    # 4. Save to database
    db.add(new_user)
    db.commit()

    # 5. Get generated fields like id
    db.refresh(new_user)

    # 6. Return the user
    return new_user

@router.post("/login",response_model=Token)  
def login(login_data:LoginRequest,db:Session=Depends(get_db)):
    user=authenticate_user(db,login_data.email,login_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Incorrect email or password given")
    access_token=create_access_token(data={"sub":user.email})    
    return{"access_token":access_token,
    "token_type":"bearer"}

# below code is to know who is the current logged in user and the token bearer
@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user


"""@router.get("/admin-test")
def admin_test(
    current_user: User = Depends(
        require_role(UserRole.ADMIN)
    )
):
    return {"message": "Admin access granted"}  """  