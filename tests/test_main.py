import pytest
from fastapi.testclient import TestClient
from main import app
from faker import Faker
import random
import uuid

client = TestClient(app)
fake = Faker('ko_KR')

# === [Helper] 테스트용 유저 생성 및 토큰 발급 함수 ===
def get_auth_headers(role="ROLE_USER"):
    """
    매번 새로운 유저를 가입시키고 로그인하여
    Authorization 헤더를 반환하는 도우미 함수
    """
    # [수정] UUID를 써서 절대로 중복되지 않는 이메일 생성
    email = f"test_{uuid.uuid4()}@example.com"
    password = "password123"
    
    # 1. 회원가입
    signup_response = client.post("/api/v1/users/signup", json={
        "email": email,
        "password": password,
        "name": fake.name(),
        "address": fake.address(),
        "phone_number": fake.phone_number(),
        "gender": "MALE",
        "role": role 
    })
    
    # 혹시라도 가입 실패하면 이유를 출력해서 디버깅 (테스트 중단)
    if signup_response.status_code != 201:
        print(f"Signup Failed: {signup_response.json()}")
        assert signup_response.status_code == 201

    # 2. 로그인
    response = client.post("/api/v1/auth/login", data={
        "username": email,
        "password": password
    })
    
    # 로그인 실패 시 중단
    assert response.status_code == 200, f"Login failed: {response.text}"
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# ==========================================
# 1. 공통 및 인증 (Auth) 테스트 (5개)
# ==========================================

def test_health_check():
    """1. 헬스체크 API가 200 OK를 반환하는지"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_signup_success():
    """2. 회원가입 성공 테스트"""
    payload = {
        "email": fake.email(),
        "password": "strongpassword",
        "name": "테스트유저",
        "gender": "FEMALE"
    }
    response = client.post("/api/v1/users/signup", json=payload)
    assert response.status_code == 201
    assert response.json()["email"] == payload["email"]

def test_signup_duplicate_email():
    """3. 중복된 이메일로 가입 시 400 에러 발생"""
    email = fake.email()
    # 첫 번째 가입
    client.post("/api/v1/users/signup", json={
        "email": email, "password": "pw", "name": "u1"
    })
    # 두 번째 가입 (중복)
    response = client.post("/api/v1/users/signup", json={
        "email": email, "password": "pw", "name": "u2"
    })
    assert response.status_code == 400

def test_login_success():
    """4. 로그인 성공 시 토큰 발급 확인"""
    # 유저 생성 및 헤더 받기 내부 로직 테스트
    headers = get_auth_headers()
    assert "Authorization" in headers
    assert headers["Authorization"].startswith("Bearer ")

def test_login_fail_wrong_password():
    """5. 비밀번호 틀렸을 때 401 에러"""
    # 먼저 유저 가입
    email = fake.email()
    client.post("/api/v1/users/signup", json={
        "email": email, "password": "real_password", "name": "fail_test"
    })
    # 틀린 비번으로 로그인
    response = client.post("/api/v1/auth/login", data={
        "username": email,
        "password": "wrong_password"
    })
    assert response.status_code == 401

# ==========================================
# 2. 회원 관리 (User) 테스트 (3개)
# ==========================================

def test_read_users_me():
    """6. 내 정보 조회 (토큰 필요)"""
    headers = get_auth_headers()
    response = client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 200
    assert "email" in response.json()

def test_read_users_me_unauthorized():
    """7. 토큰 없이 내 정보 조회 시 401 에러"""
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401

def test_update_user_me():
    """8. 내 정보 수정"""
    headers = get_auth_headers()
    new_phone = "010-0000-0000"
    response = client.patch("/api/v1/users/me", json={"phone_number": new_phone}, headers=headers)
    assert response.status_code == 200
    assert response.json()["phone_number"] == new_phone

# ==========================================
# 3. 도서 관리 (Book) 테스트 (4개)
# ==========================================

def get_valid_book_id():
    response = client.get("/api/v1/books?page=1&size=1")
    data = response.json()
    if data["books"]:
        return data["books"][0]["id"]
    return None

def test_read_books_list():
    """9. 도서 목록 조회 (페이지네이션)"""
    response = client.get("/api/v1/books?page=1&size=5")
    assert response.status_code == 200
    data = response.json()
    assert "books" in data
    assert isinstance(data["books"], list)

def test_read_book_detail_success():
    book_id = get_valid_book_id()
    if not book_id:
        pytest.skip("DB에 책이 없습니다. seed.py를 실행하세요.")
        
    response = client.get(f"/api/v1/books/{book_id}")
    assert response.status_code == 200
    assert response.json()["id"] == book_id

def test_read_book_not_found():
    """11. 없는 도서 조회 시 404 에러"""
    response = client.get("/api/v1/books/99999999")
    assert response.status_code == 404

def test_search_books():
    """12. 도서 검색 기능"""
    # 검색어가 포함된 결과가 나오거나, 없으면 빈 리스트여야 함 (에러 안나는지 확인)
    response = client.get("/api/v1/books?keyword=파이썬")
    assert response.status_code == 200

# ==========================================
# 4. 장바구니 & 주문 (Cart/Order) 테스트 (4개)
# ==========================================

# 13. 장바구니 담기 (수정됨)
def test_add_to_cart():
    headers = get_auth_headers()
    book_id = get_valid_book_id() # 동적으로 ID 가져오기
    if not book_id:
        pytest.fail("테스트할 책이 없습니다.")

    response = client.post("/api/v1/cart/", json={"book_id": book_id, "quantity": 2}, headers=headers)
    assert response.status_code == 201
    assert response.json()["quantity"] == 2

# 14. 내 장바구니 조회 (수정됨)
def test_read_cart():
    headers = get_auth_headers()
    book_id = get_valid_book_id()
    
    # 먼저 하나 담고
    client.post("/api/v1/cart/", json={"book_id": book_id, "quantity": 1}, headers=headers)
    # 조회
    response = client.get("/api/v1/cart/", headers=headers)
    assert response.status_code == 200
    assert len(response.json()["items"]) > 0

def test_create_order_empty_cart():
    """15. 빈 장바구니로 주문 시 400 에러"""
    headers = get_auth_headers()
    # 장바구니에 아무것도 안 담고 바로 주문
    payload = {
        "recipient_name": "홍길동",
        "recipient_phone": "010-1234-5678",
        "shipping_address": "서울"
    }
    response = client.post("/api/v1/orders/", json=payload, headers=headers)
    assert response.status_code == 400 # 장바구니 비어있음
    
# 16. 정상 주문 생성 (수정됨)
def test_create_order_success():
    headers = get_auth_headers()
    book_id = get_valid_book_id()

    # 1. 장바구니 담기
    client.post("/api/v1/cart/", json={"book_id": book_id, "quantity": 1}, headers=headers)
    
    # 2. 주문하기
    payload = {
        "recipient_name": "테스터",
        "recipient_phone": "010-1234-5678",
        "shipping_address": "부산"
    }
    response = client.post("/api/v1/orders/", json=payload, headers=headers)
    assert response.status_code == 201
    assert response.json()["status"] == "CREATED"

# ==========================================
# 5. 리뷰 및 기타 기능 테스트 (4개)
# ==========================================

# 17. 리뷰 작성 (수정됨)
def test_create_review():
    headers = get_auth_headers()
    book_id = get_valid_book_id()
    payload = {"rating": 5, "content": "아주 좋은 책입니다!"}
    
    response = client.post(f"/api/v1/books/{book_id}/reviews", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["rating"] == 5

# 18. 리뷰 목록 조회 (수정됨)
def test_read_reviews():
    book_id = get_valid_book_id()
    response = client.get(f"/api/v1/books/{book_id}/reviews")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# 19. 좋아요 토글 (수정됨)
def test_toggle_favorite():
    headers = get_auth_headers()
    book_id = get_valid_book_id()
    response = client.post(f"/api/v1/books/{book_id}/favorites", headers=headers)
    assert response.status_code == 200

# 20. 내가 찜한 목록 보기 (수정됨)
def test_read_my_favorites():
    headers = get_auth_headers()
    book_id = get_valid_book_id()
    client.post(f"/api/v1/books/{book_id}/favorites", headers=headers)
    
    response = client.get("/api/v1/favorites", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# ==========================================
# 6. 관리자 권한 (Admin) 테스트 (2개)
# ==========================================

def test_admin_stats_forbidden_for_user():
    """21. 일반 유저가 관리자 통계 접근 시 403 Forbidden"""
    headers = get_auth_headers(role="ROLE_USER")
    response = client.get("/api/v1/stats/daily", headers=headers)
    assert response.status_code == 403 # 권한 없음

def test_404_on_weird_url():
    """22. 이상한 URL 호출 시 표준 404 에러"""
    response = client.get("/api/v1/weird/endpoint")
    assert response.status_code == 404