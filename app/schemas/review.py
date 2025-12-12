from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="평점 (1~5)")
    content: str = Field(..., min_length=1, description="리뷰 내용")

class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    content: Optional[str] = None

class ReviewResponse(BaseModel):
    id: int
    user_id: int
    book_id: int
    rating: int
    content: str
    created_at: datetime
    # 작성자 이름도 보여주면 좋음 (선택사항)
    
    class Config:
        from_attributes = True