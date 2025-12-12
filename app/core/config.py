from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "JCloud Bookstore"
    
    # .env 파일에서 읽어올 변수들
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    DATABASE_URL: str
    
    # 토큰 유효기간 (분 단위) - 기본값 30분 설정 추가!
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    class Config:
        env_file = ".env"

settings = Settings()