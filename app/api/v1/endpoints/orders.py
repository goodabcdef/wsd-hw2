from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.order import Order, OrderItem, OrderStatus
from app.models.cart import CartItem
from app.models.user import User
from app.schemas.order import OrderCreate, OrderResponse
from app.api import deps

router = APIRouter()

# 1. 주문 생성 (장바구니에 있는 걸 주문하기)
@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_in: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    # 1. 내 장바구니 가져오기
    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    
    if not cart_items:
        raise HTTPException(status_code=400, detail="장바구니가 비어있습니다.")
    
    # 2. 총 금액 계산
    total_price = sum(item.book.price * item.quantity for item in cart_items)
    
    # 3. 주문서(Order) 만들기
    new_order = Order(
        user_id=current_user.id,
        total_price=total_price,
        status=OrderStatus.CREATED,
        recipient_name=order_in.recipient_name,
        recipient_phone=order_in.recipient_phone,
        shipping_address=order_in.shipping_address
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order) # ID 생성됨
    
    # 4. 주문 상세(OrderItem) 옮기기
    for item in cart_items:
        order_item = OrderItem(
            order_id=new_order.id,
            book_id=item.book_id,
            quantity=item.quantity,
            price_at_purchase=item.book.price # 구매 당시 가격 저장
        )
        db.add(order_item)
    
    # 5. 장바구니 비우기
    db.query(CartItem).filter(CartItem.user_id == current_user.id).delete()
    
    db.commit()
    db.refresh(new_order)
    return new_order

# 2. 내 주문 목록 조회
@router.get("/", response_model=List[OrderResponse])
def read_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    orders = db.query(Order).filter(Order.user_id == current_user.id).all()
    return orders

# 3. 주문 상세 조회
@router.get("/{order_id}", response_model=OrderResponse)
def read_order_detail(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다.")
    
    return order
    
# 4. 주문 취소 (선택 기능)
@router.post("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다.")
        
    if order.status != OrderStatus.CREATED:
         raise HTTPException(status_code=400, detail="이미 처리가 진행된 주문은 취소할 수 없습니다.")
         
    order.status = OrderStatus.CANCELED
    db.commit()
    db.refresh(order)
    return order