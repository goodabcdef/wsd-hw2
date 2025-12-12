from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from app.db.session import Base
import enum

# 성별 열거형 정의 (DB 명세서 반영)
class Gender(str, enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"

# 회원 테이블 정의
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False) # 이메일 (로그인ID)
    password_hash = Column(String(255), nullable=False) # 암호화된 비밀번호
    name = Column(String(100), nullable=False)          # 이름
    birth_date = Column(String(20))                     # 생년월일
    gender = Column(Enum(Gender), nullable=True)        # 성별
    address = Column(String(255))                       # 주소
    phone_number = Column(String(20))                   # 연락처
    role = Column(String(20), default="ROLE_USER")      # 권한 (ROLE_USER, ROLE_ADMIN)
    
    is_active = Column(Boolean, default=True)           # 계정 활성 여부
    created_at = Column(DateTime(timezone=True), server_default=func.now()) # 가입일
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())       # 수정일