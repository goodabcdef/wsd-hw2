from sqlalchemy import Column, Integer, String, Text, DateTime, DECIMAL
from sqlalchemy.sql import func
from app.db.session import Base

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True) # 제목
    # 저자와 카테고리는 여러 개일 수 있으므로 쉼표(,)로 구분된 문자열이나 JSON으로 저장
    authors = Column(Text)       # 예: "홍길동,김철수"
    categories = Column(Text)    # 예: "IT,컴퓨터"
    
    publisher = Column(String(100))        # 출판사
    publication_date = Column(String(20))  # 출판일
    isbn = Column(String(20), unique=True, index=True) # ISBN (고유번호)
    price = Column(DECIMAL(10, 2))         # 가격
    description = Column(Text)             # 상세 설명
    stock_quantity = Column(Integer, default=0) # 재고 수량
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())