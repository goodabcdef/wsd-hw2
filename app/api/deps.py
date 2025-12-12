from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from pydantic import ValidationError

from app.db.session import get_db
from app.models.user import User
from app.core.config import settings

# 토큰을 어디서 얻어오는지 설정 (로그인 API 주소)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# 1. 토큰이 유효한지 검사하고, 현재 접속한 유저 정보를 가져오는 함수
def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    try:
        # 토큰 복호화 (암호 해독)
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        # 토큰 안에 들어있는 user_id(sub) 꺼내기
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="자격 증명을 확인할 수 없습니다.",
            )
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="자격 증명을 확인할 수 없습니다.",
        )
    
    # DB에서 유저 찾기
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    
    return user

# 2. 관리자(Admin) 권한인지 체크하는 함수
def check_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != "ROLE_ADMIN":
        raise HTTPException(
            status_code=403, 
            detail="관리자 권한이 필요합니다."
        )
    return current_user