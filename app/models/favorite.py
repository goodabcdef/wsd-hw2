from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base

class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 한 사람이 같은 책을 두 번 찜할 수 없도록 유니크 제약
    __table_args__ = (
        UniqueConstraint('user_id', 'book_id', name='uq_user_book_favorite'),
    )

    book = relationship("Book")