from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.db.session import get_db
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.core.config import settings
from app.models.user import User
from app.schemas.token import Token, TokenRefreshRequest
from app.api import deps # get_current_user 사용을 위해

router = APIRouter()

# 1. 로그인 (토큰 발급) - 수정됨
@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 잘못되었습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Access Token 생성 (짧은 수명)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role},
        expires_delta=access_token_expires
    )
    
    # [추가] Refresh Token 생성 (긴 수명)
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)}, # 보통 role 정보는 뺍니다
        expires_delta=refresh_token_expires
    )
    
    return {
        "access_token": access_token, 
        "refresh_token": refresh_token, 
        "token_type": "bearer"
    }

# 2. 토큰 재발급 (Refresh) - 신규
@router.post("/refresh", response_model=Token)
def refresh_token(
    request: TokenRefreshRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh Token을 검증하여 새로운 Access Token을 발급합니다.
    """
    try:
        # 토큰 디코딩
        payload = jwt.decode(
            request.refresh_token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        # 토큰 타입 확인 (access 토큰을 refresh에 넣는 것 방지)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="유효하지 않은 토큰 타입입니다.")
            
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")
            
        # 유저가 실제로 존재하는지 확인
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
            
        # 새로운 Access Token 발급
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        new_access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role},
            expires_delta=access_token_expires
        )
        
        # Refresh Token은 그대로 돌려주거나(Rotation 안 함), 새로 발급해줄 수 있음.
        # 여기서는 Access Token만 갱신하고 Refresh Token은 기존 것을 그대로 사용한다고 가정
        # (만약 Refresh Token도 갱신하려면 위 create_refresh_token 로직 반복)
        
        return {
            "access_token": new_access_token,
            "refresh_token": request.refresh_token, # 기존 토큰 유지
            "token_type": "bearer"
        }
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh Token이 만료되었거나 유효하지 않습니다."
        )

# 3. 로그아웃 (Logout) - 신규
@router.post("/logout")
def logout(current_user: User = Depends(deps.get_current_user)):
    """
    로그아웃 처리.
    JWT는 서버에 저장되지 않으므로(Stateless), 
    서버 측에서는 '성공' 응답만 주고 
    클라이언트(프론트엔드)에서 로컬 스토리지의 토큰을 삭제해야 합니다.
    """
    # 더 강력한 보안을 위해선 Redis 같은 곳에 토큰을 블랙리스트로 등록해야 하지만,
    # 지금 과제 수준에서는 클라이언트에게 삭제를 위임하는 방식으로 처리합니다.
    return {"message": "로그아웃 되었습니다. 클라이언트에서 토큰을 삭제해주세요."}