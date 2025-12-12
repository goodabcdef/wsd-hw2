from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# 공통 필드
class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="책 제목")
    authors: str = Field(..., description="저자 목록 (콤마로 구분)")
    categories: str = Field(..., description="카테고리 (콤마로 구분)")
    publisher: Optional[str] = None
    publication_date: Optional[str] = None
    isbn: str = Field(..., description="ISBN 번호")
    price: float = Field(..., ge=0, description="가격")
    description: Optional[str] = None
    stock_quantity: int = Field(0, ge=0, description="재고 수량")

# 생성 요청 (Create)
class BookCreate(BookBase):
    pass

# 수정 요청 (Update) - 모든 필드가 선택적(Optional)
class BookUpdate(BaseModel):
    title: Optional[str] = None
    authors: Optional[str] = None
    categories: Optional[str] = None
    publisher: Optional[str] = None
    publication_date: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    stock_quantity: Optional[int] = None
    # ISBN은 수정 불가로 설정

# 응답 (Response)
class BookResponse(BookBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# 목록 조회 응답 (List)
class BookListResponse(BaseModel):
    total_count: int
    current_page: int
    total_pages: int
    books: List[BookResponse]