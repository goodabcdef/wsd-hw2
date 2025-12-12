from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime

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
class BookResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    authors: Optional[str] = None
    publisher: Optional[str] = None
    publication_date: Optional[date] = None
    price: int
    stock: int
    categories: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 목록 조회 응답 (List)
class BookListResponse(BaseModel):
    content: List[BookResponse]  # books -> content
    page: int                    # current_page -> page
    size: int
    totalElements: int           # total_count -> totalElements
    totalPages: int              # total_pages -> totalPages
    sort: str                    # 정렬 정보 추가