# app/api/v1/endpoints/stats.py
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.db.session import get_db
from app.models.order import Order, OrderItem
from app.models.book import Book
from app.models.user import User
from app.api import deps
from app.schemas.stats import DailySalesResponse, TopSellerResponse # 스키마 임포트

router = APIRouter()

# 1. 일별 매출 통계
@router.get("/daily", response_model=List[DailySalesResponse])
def get_daily_sales(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.check_admin)
):
    # 날짜별 그룹핑 쿼리
    results = db.query(
        func.date(Order.created_at).label("date"),
        func.sum(Order.total_price).label("total_sales"),
        func.count(Order.id).label("order_count")
    ).group_by(func.date(Order.created_at)).all()
    
    # [수정된 부분] SQLAlchemy Row 객체를 Pydantic 스키마에 맞는 dict로 변환
    response_data = []
    for r in results:
        response_data.append({
            "date": str(r.date) if r.date else "",
            # Decimal 타입이 나올 수 있으므로 float으로 변환, 없으면 0
            "total_sales": float(r.total_sales) if r.total_sales else 0.0,
            "order_count": int(r.order_count)
        })
    
    return response_data

# 2. 많이 팔린 책 순위
@router.get("/top-sellers", response_model=List[TopSellerResponse])
def get_top_sellers(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.check_admin)
):
    results = db.query(
        Book.title,
        func.sum(OrderItem.quantity).label("total_sold")
    ).join(Book, OrderItem.book_id == Book.id)\
     .group_by(Book.id)\
     .order_by(desc("total_sold"))\
     .limit(limit).all()
     
    # [수정된 부분] 명시적 형변환
    response_data = []
    for r in results:
        response_data.append({
            "title": r.title,
            # sum 결과가 None일 경우 대비
            "total_sold": int(r.total_sold) if r.total_sold else 0
        })

    return response_data