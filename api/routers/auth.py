from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from schemas.schemas import UserCreate, UserResponse, BaseResponse
from models.models import User
from core.security import get_password_hash, create_access_token, verify_password
from api.dependencies import get_db

router = APIRouter()

@router.post("/signup", response_model=BaseResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        return BaseResponse(success=False, message="Email already registered", errors=["Email exists"])
    hashed_password = get_password_hash(user.password)
    db_user = User(
        name=user.name,
        email=user.email,
        password=hashed_password,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return BaseResponse(success=True, message="User created successfully", object=UserResponse.from_orm(db_user).dict())

@router.post("/login", response_model=BaseResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        return BaseResponse(success=False, message="Invalid credentials", errors=["Invalid email or password"])
    access_token = create_access_token(data={"sub": user.email})
    return BaseResponse(success=True, message="Login successful", object={"access_token": access_token, "token_type": "bearer"})