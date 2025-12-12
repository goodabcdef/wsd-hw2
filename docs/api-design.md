# 📘 API 설계서 (API Design)

## 1. 개요
JCloud Bookstore 서비스의 RESTful API 명세입니다.

## 2. API 목록

### 🔐 인증 (Auth)
| Method | URI | 설명 |
| :--- | :--- | :--- |
| `POST` | `/api/v1/users/signup` | 회원가입 |
| `POST` | `/api/v1/auth/login` | 로그인 (Access/Refresh Token 발급) |
| `POST` | `/api/v1/auth/refresh` | 토큰 재발급 |
| `POST` | `/api/v1/auth/logout` | 로그아웃 |

### 👤 회원 (Users)
| Method | URI | 설명 | 권한 |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/users/me` | 내 정보 조회 | User |
| `PATCH` | `/api/v1/users/me` | 내 정보 수정 | User |
| `DELETE` | `/api/v1/users/me` | 회원 탈퇴 | User |
| `GET` | `/api/v1/users/` | [관리자] 전체 회원 조회 | Admin |
| `PATCH` | `/api/v1/users/{id}/status` | [관리자] 회원 정지/해제 | Admin |

### 📖 도서 (Books)
| Method | URI | 설명 | 권한 |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/books/` | 도서 목록 조회 (검색, 정렬, 페이징) | All |
| `GET` | `/api/v1/books/{id}` | 도서 상세 조회 | All |
| `POST` | `/api/v1/books/` | [관리자] 도서 등록 | Admin |
| `PATCH` | `/api/v1/books/{id}` | [관리자] 도서 수정 | Admin |
| `DELETE` | `/api/v1/books/{id}` | [관리자] 도서 삭제 | Admin |

### 🛒 장바구니 & 주문 (Cart & Order)
| Method | URI | 설명 |
| :--- | :--- | :--- |
| `GET` | `/api/v1/cart/` | 내 장바구니 조회 |
| `POST` | `/api/v1/cart/` | 장바구니 담기 |
| `PATCH` | `/api/v1/cart/{id}` | 수량 변경 |
| `DELETE` | `/api/v1/cart/{id}` | 삭제 |
| `POST` | `/api/v1/orders/` | 주문 생성 |
| `GET` | `/api/v1/orders/` | 내 주문 내역 조회 |

### ❤️ 리뷰 & 좋아요
| Method | URI | 설명 |
| :--- | :--- | :--- |
| `POST` | `/api/v1/books/{id}/reviews` | 리뷰 작성 |
| `POST` | `/api/v1/books/{id}/favorites` | 좋아요 (Toggle) |
| `GET` | `/api/v1/favorites` | 찜한 목록 보기 |