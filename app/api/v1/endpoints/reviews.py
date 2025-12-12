from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.review import Review
from app.models.book import Book
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewResponse
from app.api import deps

router = APIRouter()

# 1. 리뷰 작성
@router.post("/books/{book_id}/reviews", response_model=ReviewResponse)
def create_review(
    book_id: int,
    review_in: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    # 책 존재 여부 확인
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="책을 찾을 수 없습니다.")

    new_review = Review(
        user_id=current_user.id,
        book_id=book_id,
        rating=review_in.rating,
        content=review_in.content
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review

# 2. 해당 책의 리뷰 목록 조회
@router.get("/books/{book_id}/reviews", response_model=List[ReviewResponse])
def read_reviews(book_id: int, db: Session = Depends(get_db)):
    reviews = db.query(Review).filter(Review.book_id == book_id).all()
    return reviews

# 3. 리뷰 수정 (본인만)
@router.patch("/reviews/{review_id}", response_model=ReviewResponse)
def update_review(
    review_id: int,
    review_in: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="리뷰를 찾을 수 없습니다.")
    if review.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="본인의 리뷰만 수정할 수 있습니다.")

    if review_in.rating:
        review.rating = review_in.rating
    if review_in.content:
        review.content = review_in.content
        
    db.commit()
    db.refresh(review)
    return review

# 4. 리뷰 삭제 (본인 혹은 관리자)
@router.delete("/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="리뷰를 찾을 수 없습니다.")
    
    # 관리자이거나 본인이면 삭제 허용
    if current_user.role != "ROLE_ADMIN" and review.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
        
    db.delete(review)
    db.commit()
    return None