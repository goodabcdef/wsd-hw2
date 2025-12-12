from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.favorite import Favorite
from app.models.book import Book
from app.models.user import User
from app.schemas.book import BookResponse # 책 정보를 보여주기 위해 재사용
from app.api import deps

router = APIRouter()

# 1. 좋아요 누르기/취소 (Toggle 방식)
@router.post("/books/{book_id}/favorites")
def toggle_favorite(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="책을 찾을 수 없습니다.")

    # 이미 찜했는지 확인
    existing_fav = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.book_id == book_id
    ).first()

    if existing_fav:
        # 있으면 삭제 (좋아요 취소)
        db.delete(existing_fav)
        db.commit()
        return {"message": "좋아요 취소", "liked": False}
    else:
        # 없으면 추가 (좋아요)
        new_fav = Favorite(user_id=current_user.id, book_id=book_id)
        db.add(new_fav)
        db.commit()
        return {"message": "좋아요 등록", "liked": True}

# 2. 내가 찜한 목록 보기
@router.get("/favorites", response_model=List[BookResponse])
def read_my_favorites(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    # Favorite 테이블을 통해 Book 정보를 조인해서 가져옴
    favorites = db.query(Favorite).filter(Favorite.user_id == current_user.id).all()
    # Favorite 객체 안에 relationship으로 연결된 book을 리스트로 반환
    return [fav.book for fav in favorites]