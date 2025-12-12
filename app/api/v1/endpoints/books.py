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
    # [수정] 정렬 규격: field,ASC|DESC
    sort: str = Query("created_at,desc", description="정렬: field,asc|desc (예: price,asc)"),
    # [수정] 검색 필터 1: 통합 검색
    keyword: Optional[str] = Query(None, description="검색어 (제목, 저자)"),
    # [추가] 검색 필터 2: 카테고리 (최소 2개 조건 만족용)
    category: Optional[str] = Query(None, description="카테고리 필터")
):
    query = db.query(Book)
    
    # 1. 필터링 (Where)
    if keyword:
        search = f"%{keyword}%"
        query = query.filter(
            or_(
                Book.title.like(search),
                Book.authors.like(search)
            )
        )
    
    if category:
        query = query.filter(Book.categories.like(f"%{category}%"))
    
    # 2. 정렬 (Sorting) - "price,desc" 파싱
    try:
        sort_field, sort_dir = sort.split(",")
        sort_field = sort_field.strip()
        sort_dir = sort_dir.strip().lower()
    except ValueError:
        # 포맷이 안 맞으면 기본값 적용
        sort_field = "created_at"
        sort_dir = "desc"

    # DB 컬럼 매핑 (보안상 허용된 컬럼만 정렬 가능하게 함)
    allowed_sort_fields = {
        "price": Book.price,
        "title": Book.title,
        "created_at": Book.created_at,
        "id": Book.id
    }
    
    target_column = allowed_sort_fields.get(sort_field, Book.created_at)
    
    if sort_dir == "asc":
        query = query.order_by(asc(target_column))
    else:
        query = query.order_by(desc(target_column))
        
    # 3. 페이지네이션 (Pagination)
    total_elements = query.count()
    total_pages = ceil(total_elements / size)
    
    offset = (page - 1) * size
    books = query.offset(offset).limit(size).all()
    
    # 4. 응답 생성 (규격 맞춤)
    return {
        "content": books,
        "page": page,
        "size": size,
        "totalElements": total_elements,
        "totalPages": total_pages,
        "sort": sort # 요청받은 정렬 문자열 그대로 반환
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