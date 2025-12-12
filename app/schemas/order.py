from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.schemas.book import BookResponse

# 주문 생성 요청 (배송지 정보만 받음. 물건은 장바구니에서 가져옴)
class OrderCreate(BaseModel):
    recipient_name: str
    recipient_phone: str
    shipping_address: str

# 주문 상세 품목 응답
class OrderItemResponse(BaseModel):
    book_id: int
    quantity: int
    price_at_purchase: float
    book: BookResponse # 어떤 책인지 정보 포함

    class Config:
        from_attributes = True

# 주문서 응답
class OrderResponse(BaseModel):
    id: int
    status: str
    total_price: float
    recipient_name: str
    shipping_address: str
    created_at: datetime
    items: List[OrderItemResponse] # 하위 품목들

    class Config:
        from_attributes = True