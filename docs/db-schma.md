# 🗄️ 데이터베이스 스키마 (DB Schema)

## ERD 개요
사용자(User), 도서(Book)를 중심으로 주문(Order), 장바구니(Cart), 리뷰(Review)가 연결된 관계형 구조입니다.

## 테이블 명세

### 1. Users (사용자)
- **id** (PK): BIGINT, Auto Increment
- **email**: VARCHAR, Unique (로그인 ID)
- **password_hash**: VARCHAR
- **role**: VARCHAR (ROLE_USER, ROLE_ADMIN)
- **is_active**: BOOLEAN

### 2. Books (도서)
- **id** (PK): BIGINT
- **title**: VARCHAR
- **price**: INTEGER
- **stock**: INTEGER
- **category**: VARCHAR

### 3. CartItems (장바구니)
- **id** (PK): BIGINT
- **user_id** (FK): Users.id
- **book_id** (FK): Books.id
- **quantity**: INTEGER

### 4. Orders (주문)
- **id** (PK): BIGINT
- **user_id** (FK): Users.id
- **total_price**: INTEGER
- **status**: VARCHAR (CREATED, PAID, CANCELED)

### 5. OrderItems (주문 상세)
- **id** (PK): BIGINT
- **order_id** (FK): Orders.id
- **book_id** (FK): Books.id
- **price_at_purchase**: INTEGER

### 6. Reviews / Favorites
- 사용자와 도서 간의 1:N 또는 N:M 관계 매핑