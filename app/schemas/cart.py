from pydantic import BaseModel
from typing import List
from app.schemas.book import BookResponse  # 책 정보를 보여주기 위해 가져옴

# 장바구니 담기 요청
class CartItemCreate(BaseModel):
    book_id: int
    quantity: int = 1

# 수량 수정 요청
class CartItemUpdate(BaseModel):
    quantity: int

# 장바구니 조회 응답 (책 정보 포함)
class CartItemResponse(BaseModel):
    id: int
    quantity: int
    book: BookResponse  # 책 상세 정보가 통째로 들어감

    class Config:
        from_attributes = True

# 전체 장바구니 목록 응답
class CartListResponse(BaseModel):
    items: List[CartItemResponse]
    total_price: float  # 총 주문 금액 계산해서 보여줌