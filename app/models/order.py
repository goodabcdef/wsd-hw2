import enum
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, DECIMAL, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base

# 주문 상태 정의 (DB 명세서 반영)
class OrderStatus(str, enum.Enum):
    CREATED = "CREATED"     # 주문 생성됨
    PAID = "PAID"           # 결제 완료
    CANCELED = "CANCELED"   # 주문 취소
    SHIPPED = "SHIPPED"     # 배송 중
    DELIVERED = "DELIVERED" # 배송 완료

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    total_price = Column(DECIMAL(10, 2), nullable=False) # 총 결제 금액
    status = Column(Enum(OrderStatus), default=OrderStatus.CREATED)
    
    recipient_name = Column(String(100))    # 받는 사람 이름
    recipient_phone = Column(String(20))    # 받는 사람 전화번호
    shipping_address = Column(String(255))  # 배송지 주소
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 관계 설정
    items = relationship("OrderItem", back_populates="order")
    user = relationship("User")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    
    quantity = Column(Integer, nullable=False)     # 주문 수량
    price_at_purchase = Column(DECIMAL(10, 2))     # 구매 당시 가격 (가격 변동 대비)
    
    # 관계 설정
    order = relationship("Order", back_populates="items")
    book = relationship("Book")