from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum

# 성별 선택지 정의
class Gender(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"

# 유저가 회원가입할 때 보내는 데이터
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    address: Optional[str] = None
    phone_number: Optional[str] = None
    gender: Optional[Gender] = None  # 여기를 str 대신 Gender로 변경!

# 응답으로 보여줄 데이터
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    name: str
    is_active: bool
    phone_number: Optional[str] = None
    address: Optional[str] = None
    gender: Optional[str] = None
    role: str

    class Config:
        from_attributes = True
        

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
    # 내 정보 수정용 (비밀번호, 주소, 전화번호만 변경 가능하다고 가정)
class UserUpdate(BaseModel):
    password: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None

# 관리자용 회원 상태 변경
class UserStatusUpdate(BaseModel):
    is_active: bool