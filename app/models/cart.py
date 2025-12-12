from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base

class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    
    # 누가 담았는지 (User 테이블과 연결)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 어떤 책인지 (Book 테이블과 연결)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    
    # 몇 권인지
    quantity = Column(Integer, default=1)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 관계 설정 (DB에서 책 정보를 바로 가져오기 위함)
    book = relationship("Book")
    user = relationship("User")