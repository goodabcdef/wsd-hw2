from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.cart import CartItem
from app.models.book import Book
from app.models.user import User
from app.schemas.cart import CartItemCreate, CartItemUpdate, CartItemResponse, CartListResponse
from app.api import deps  # 로그인 체크용

router = APIRouter()

# 1. 장바구니 담기 (POST)
@router.post("/", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
def add_to_cart(
    cart_in: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user) # 로그인 필수
):
    # 책이 진짜 있는지 확인
    book = db.query(Book).filter(Book.id == cart_in.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="존재하지 않는 책입니다.")

    # 이미 장바구니에 담긴 책인지 확인
    existing_item = db.query(CartItem).filter(
        CartItem.user_id == current_user.id,
        CartItem.book_id == cart_in.book_id
    ).first()

    if existing_item:
        # 이미 있으면 수량만 추가
        existing_item.quantity += cart_in.quantity
        db.commit()
        db.refresh(existing_item)
        return existing_item
    else:
        # 없으면 새로 생성
        new_item = CartItem(
            user_id=current_user.id,
            book_id=cart_in.book_id,
            quantity=cart_in.quantity
        )
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return new_item

# 2. 내 장바구니 조회 (GET)
@router.get("/", response_model=CartListResponse)
def read_my_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    # 내 장바구니 목록 가져오기
    items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    
    # 총 금액 계산 (책 가격 * 수량)
    total_price = sum(item.book.price * item.quantity for item in items)
    
    return {"items": items, "total_price": total_price}

# 3. 수량 변경 (PATCH)
@router.patch("/{item_id}", response_model=CartItemResponse)
def update_cart_item(
    item_id: int,
    cart_update: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    item = db.query(CartItem).filter(
        CartItem.id == item_id, 
        CartItem.user_id == current_user.id # 내 장바구니인지 확인
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="장바구니 아이템을 찾을 수 없습니다.")
        
    if cart_update.quantity <= 0:
        # 수량이 0 이하면 삭제
        db.delete(item)
        db.commit()
        # 삭제된 경우 빈 객체 반환은 애매하므로, 여기선 그냥 에러나 메시지를 주는게 낫지만 로직상 일단 진행
        return item 
    
    item.quantity = cart_update.quantity
    db.commit()
    db.refresh(item)
    return item

# 4. 장바구니 삭제 (DELETE)
@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_cart(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="장바구니 아이템을 찾을 수 없습니다.")
        
    db.delete(item)
    db.commit()
    return None