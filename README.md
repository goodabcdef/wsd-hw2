# 📚 JCloud Bookstore API

**JCloud Bookstore**는 온라인 서점 서비스를 위한 고성능 RESTful API 서버입니다.  
FastAPI 프레임워크를 기반으로 구축되었으며, 사용자 인증, 도서 검색, 장바구니, 주문 처리, 리뷰 및 관리자 통계 기능을 제공합니다.

## 🌟 주요 기능 (Key Features)

이 프로젝트는 다음과 같은 핵심 기능을 포함합니다:

* **🔐 인증 및 인가 (Authentication & Authorization)**
    * JWT (JSON Web Token) 기반의 로그인 (Access Token + Refresh Token).
    * Role 기반 접근 제어 (`ROLE_USER`, `ROLE_ADMIN`).
    * 회원가입, 내 정보 수정, 회원 탈퇴, 로그아웃.
* **📖 도서 관리 (Book Management)**
    * 도서 목록 조회 (검색, 정렬, 페이지네이션 지원).
    * 도서 상세 조회.
    * [관리자] 도서 등록, 수정, 삭제.
* **🛒 쇼핑 프로세스 (Shopping Process)**
    * 장바구니 담기, 수량 변경, 삭제.
    * 장바구니 기반 주문 생성 및 주문 내역 조회.
    * 주문 취소 기능.
* **❤️ 소셜 및 상호작용 (Social & Interaction)**
    * 도서 '좋아요' (찜하기) 및 목록 조회.
    * 리뷰 작성, 수정, 삭제 (본인 및 관리자 권한).
* **📊 관리자 기능 (Admin Features)**
    * 일별 매출 통계 조회.
    * 판매량 기준 베스트셀러 순위 조회.
    * 전체 회원 관리 및 계정 정지/해제.
* **🛡️ 보안 및 안정성**
    * **Rate Limiting:** 하루 1000회, 분당 100회 요청 제한 (DDoS 방지).
    * **CORS:** Cross-Origin Resource Sharing 설정.
    * **Standardized Error:** 통일된 JSON 에러 응답 포맷.

---

## 🛠️ 기술 스택 (Tech Stack)

* **Language:** Python 3.9+
* **Framework:** FastAPI
* **Database ORM:** SQLAlchemy
* **Authentication:** OAuth2 (JWT), Passlib (Bcrypt)
* **Validation:** Pydantic
* **Rate Limiting:** SlowAPI

---

## 🔗 API 접속 정보 (API Endpoints)

서버가 실행 중일 때 아래 주소를 통해 API 문서를 확인하고 테스트할 수 있습니다.

| 구분 | URL | 설명 |
| :--- | :--- | :--- |
| **Swagger UI** | `http://113.198.66.68:10130/docs` | 대화형 API 문서 및 테스트 도구 |
| **ReDoc** | `http://113.198.66.68:10130/redoc` | 문서 중심의 API 명세서 |
| **API Root** | `http://113.198.66.68:10130/api/v1` | API 엔드포인트 기본 경로 |
| **Health Check** | `http://113.198.66.68:10130/health` | 서버 상태 확인 |

> **Localhost 예시:** `http://113.198.66.68:10130/docs`

---

## 🚀 설치 및 실행 방법 (Installation & Running)

이 프로젝트를 로컬 환경이나 서버에 배포하기 위한 단계입니다.


1. 프로젝트 클론 (Clone)
```bash
git clone [레포지토리 주소]
cd [프로젝트 폴더명]


2. 가상환경 생성 및 활성화 (선택 사항)
파이썬 가상환경을 사용하는 것을 권장합니다.

Windows:
python -m venv venv
.\venv\Scripts\activate

Mac/Linux:
python3 -m venv venv
source venv/bin/activate


3. 패키지 설치 (Install Dependencies)
필요한 라이브러리를 설치합니다.
pip install -r requirements.txt


4. 서버 실행 (Run Server)
main.py가 있는 위치에서 아래 명령어를 실행합니다.
# 개발 모드 (코드 수정 시 자동 재시작)
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
# 또는 python 명령어로 실행 (main.py 내부 설정 사용)
python main.py


5. 실행 확인
브라우저나 Postman을 열고 아래 주소로 접속하여 {"status": "ok", ...} 메시지가 나오는지 확인합니다.

http://localhost:8080/health

📂 프로젝트 구조 (Project Structure)
app/
├── api/
│   ├── deps.py               # 의존성 주입 (Current User, Admin Check)
│   └── v1/
│       └── endpoints/        # API 라우터 (Users, Auth, Books, Orders...)
├── core/
│   ├── config.py             # 설정 (환경변수)
│   └── security.py           # 보안 (JWT 생성, 비밀번호 해싱)
├── db/                       # 데이터베이스 세션 및 설정
├── models/                   # SQLAlchemy DB 모델 정의
├── schemas/                  # Pydantic 데이터 검증 스키마
main.py                       # 앱 진입점 (Middleware, Exception Handler)# wsd-hw2


6. API 테스트 (Postman)
이 저장소에 포함된 `JCloud_Bookstore.postman_collection.json` 파일을 Postman에서 [Import] 하시면, 미리 작성된 API 요청들을 바로 테스트해볼 수 있습니다.