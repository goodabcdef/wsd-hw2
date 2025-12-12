from math import ceil
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.session import get_db
from app.models.book import Book
from app.models.user import User
from app.schemas.book import BookCreate, BookUpdate, BookResponse, BookListResponse
from app.api import deps

router = APIRouter()

# 1. 도서 등록 (관리자만 가능)
@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(
    book: BookCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.check_admin)
):
    if db.query(Book).filter(Book.isbn == book.isbn).first():
        raise HTTPException(status_code=400, detail="이미 등록된 ISBN입니다.")
    
    new_book = Book(**book.model_dump())
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book

# 2. 도서 목록 조회 (누구나 가능)
@router.get("/", response_model=BookListResponse)
def read_books(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(10, ge=1, le=100, description="페이지 크기"),
    keyword: Optional[str] = Query(None, description="검색어"),
    sort_by: Optional[str] = Query("created_at", description="정렬 기준"),
    sort_desc: bool = Query(True, description="내림차순 여부")
):
    query = db.query(Book)
    
    # 검색 필터
    if keyword:
        search = f"%{keyword}%"
        query = query.filter(
            or_(
                Book.title.like(search),
                Book.authors.like(search),
                Book.categories.like(search)
            )
        )
    
    # 정렬 조건
    if sort_by == "price":
        order_col = Book.price
    elif sort_by == "title":
        order_col = Book.title
    else:
        order_col = Book.created_at
        
    if sort_desc:
        query = query.order_by(order_col.desc())
    else:
        query = query.order_by(order_col.asc())
        
    # 페이지네이션 계산
    total_count = query.count()
    total_pages = ceil(total_count / size)
    
    offset = (page - 1) * size
    books = query.offset(offset).limit(size).all()
    
    # [중요] 이 return 문이 꼭 있어야 하고, 들여쓰기가 def read_books와 맞아야 합니다!
    return {
        "total_count": total_count,
        "current_page": page,
        "total_pages": total_pages,
        "books": books
    }

# 3. 도서 상세 조회
@router.get("/{book_id}", response_model=BookResponse)
def read_book_detail(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="책을 찾을 수 없습니다.")
    return book

# 4. 도서 수정 (관리자만 가능)
@router.patch("/{book_id}", response_model=BookResponse)
def update_book(
    book_id: int, 
    book_update: BookUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.check_admin)
):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="책을 찾을 수 없습니다.")
    
    update_data = book_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(book, key, value)
        
    db.commit()
    db.refresh(book)
    return book

# 5. 도서 삭제 (관리자만 가능)
@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(
    book_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.check_admin)
):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="책을 찾을 수 없습니다.")
        
    db.delete(book)
    db.commit()
    return None