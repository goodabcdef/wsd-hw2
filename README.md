# 📚 JCloud Bookstore API

**JCloud Bookstore**는 온라인 서점 서비스를 위한 고성능 RESTful API 서버입니다.  
FastAPI 프레임워크를 기반으로 구축되었으며, 사용자 인증, 도서 검색, 장바구니, 주문 처리, 리뷰 및 관리자 통계 기능을 제공합니다.

---

## 🌟 주요 기능 (Key Features)

이 프로젝트는 다음과 같은 핵심 기능을 포함합니다:

* **🔐 인증 및 인가 (Authentication & Authorization)**
    * JWT (JSON Web Token) 기반의 로그인 (Access Token + Refresh Token).
    * Role 기반 접근 제어 (`ROLE_USER`, `ROLE_ADMIN`).
* **📖 도서 관리 (Book Management)**
    * 도서 목록 조회 (검색, 정렬, 페이지네이션 지원).
    * [관리자] 도서 등록, 수정, 삭제.
* **🛒 쇼핑 프로세스 (Shopping Process)**
    * 장바구니 담기, 수량 변경, 삭제.
    * 주문 생성, 내역 조회, 취소.
* **📊 관리자 기능 (Admin Features)**
    * 일별 매출 통계, 베스트셀러 순위.
    * 회원 관리 (정지/해제).
* **🛡️ 보안 및 성능**
    * **Rate Limiting:** 하루 1000회/분당 100회 제한 (SlowAPI).
    * **CORS:** 모든 도메인 허용 설정.

---

## 🛠️ 기술 스택 (Tech Stack)

* **Language:** Python 3.10+
* **Framework:** FastAPI
* **Database:** MySQL (Production), SQLite (Test)
* **ORM:** SQLAlchemy
* **Authentication:** OAuth2 (JWT), Passlib (Bcrypt)

---

## 🔗 배포 주소 (Deployment)

| 구분 | URL | 설명 |
| :--- | :--- | :--- |
| **Base URL** | `http://113.198.66.68:10130` | API 서버 주소 |
| **Swagger UI** | `http://113.198.66.68:10130/docs` | API 테스트 도구 |
| **ReDoc** | `http://113.198.66.68:10130/redoc` | API 명세서 |
| **Health Check** | `http://113.198.66.68:10130/health` | 서버 상태 확인 |

---

## 🏃 실행 방법 (Getting Started)

### 1. 프로젝트 클론 & 패키지 설치

```bash
# Clone
git clone https://github.com/[본인아이디]/jcloud-bookstore.git
cd jcloud-bookstore

# 가상환경 생성 (권장)
python3 -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경변수 설정 (.env)

프로젝트 루트에 `.env` 파일을 생성하고 아래 내용을 설정합니다.

```ini
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
SQLALCHEMY_DATABASE_URL=mysql+pymysql://user:password@localhost:3306/dbname
```

### 3. 서버 실행

```bash
# 앱 실행 (테이블 자동 생성됨)
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

---

## 🔐 인증 및 권한 (Auth & Roles)

### 인증 플로우
1. `POST /api/v1/auth/login`으로 이메일/비번 전송.
2. 응답받은 `access_token`을 HTTP Header에 포함하여 요청.

```http
Authorization: Bearer <access_token>
```

### 역할별 권한 (Permissions)

| Role | 접근 가능 범위 | 비고 |
| :--- | :--- | :--- |
| **ROLE_USER** | 도서 조회, 장바구니, 주문, 리뷰 작성, 내 정보 관리 | 일반 회원 |
| **ROLE_ADMIN** | **위 기능 포함** + 도서 CUD, 회원 관리, 통계 조회 | 관리자 |

---

## 🧪 테스트 정보 (Testing Info)

채점 및 테스트를 위한 예제 계정과 DB 정보입니다.

### 1. 예제 계정 (Test Accounts)

| Role | Email | Password |
| :--- | :--- | :--- |
| **User** | `user@example.com` | `password123` |
| **Admin** | `admin@example.com` | `admin123` |

### 2. DB 연결 정보
* **Host/Port:** `113.198.66.68:3306` (외부 접속 허용 시)
* **DB Name:** `bookstore_db`
* **User/PW:** `book_user` / `db_password`

---

## 📡 엔드포인트 요약 (Endpoints)

주요 API 목록입니다. 상세 스펙은 Swagger를 참고하세요.

| 카테고리 | Method | URL | 설명 |
| :--- | :--- | :--- | :--- |
| **Auth** | POST | `/api/v1/auth/login` | 로그인 |
| **Books** | GET | `/api/v1/books/` | 도서 목록 (검색/정렬) |
| | POST | `/api/v1/books/` | [Admin] 도서 등록 |
| **Cart** | POST | `/api/v1/cart/` | 장바구니 담기 |
| **Orders** | POST | `/api/v1/orders/` | 주문 생성 |
| **Stats** | GET | `/api/v1/stats/daily` | [Admin] 일별 매출 |

---

## ⚠️ 한계와 개선 계획 (Limitations)

* **결제 연동 부재:** 실제 PG사 연동 없이 주문 데이터만 생성됩니다. 추후 PortOne API 연동 예정.
* **동기식 DB 처리:** 트래픽 증가 시 성능 저하 우려. 추후 `async/await`를 완벽 지원하는 비동기 드라이버(`aiomysql`)로 교체 고려.
* **테스트 코드 부족:** 현재 단위 테스트 커버리지가 낮음. `pytest` 케이스 추가 예정.