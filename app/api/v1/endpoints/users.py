from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate, UserStatusUpdate
from app.core.security import get_password_hash
from app.api import deps

router = APIRouter()

# 1. 회원가입 (기존 코드 유지)
@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다.")
    hashed_password = get_password_hash(user.password)
    new_user = User(
        email=user.email, password_hash=hashed_password, name=user.name,
        address=user.address, phone_number=user.phone_number, gender=user.gender,
        role="ROLE_USER"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# 2. 내 정보 조회
@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(deps.get_current_user)):
    return current_user

# 3. 내 정보 수정
@router.patch("/me", response_model=UserResponse)
def update_user_me(
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    if user_in.password:
        current_user.password_hash = get_password_hash(user_in.password)
    if user_in.address:
        current_user.address = user_in.address
    if user_in.phone_number:
        current_user.phone_number = user_in.phone_number
        
    db.commit()
    db.refresh(current_user)
    return current_user

# 4. 회원 탈퇴
@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    db.delete(current_user)
    db.commit()
    return None

# 5. [관리자] 전체 회원 목록 조회
@router.get("/", response_model=List[UserResponse])
def read_users(
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.check_admin)
):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

# 6. [관리자] 회원 정지/해제
@router.patch("/{user_id}/status", response_model=UserResponse)
def update_user_status(
    user_id: int,
    status_in: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.check_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    
    user.is_active = status_in.is_active
    db.commit()
    db.refresh(user)
    return user