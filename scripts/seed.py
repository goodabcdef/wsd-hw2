# scripts/seed.py
import sys
import os
# 프로젝트 루트 경로를 잡아주기 위함
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.models.book import Book
from app.models.review import Review
from app.core.security import get_password_hash
from faker import Faker
import random

fake = Faker('ko_KR') # 한국어 데이터 생성

def seed_data():
    db = SessionLocal()
    
    print("🌱 데이터 생성을 시작합니다...")

    # 1. 유저 20명 생성
    users = []
    # 관리자 1명
    admin = User(
        email="admin@example.com",
        password_hash=get_password_hash("admin123"),
        name="관리자",
        role="ROLE_ADMIN"
    )
    db.add(admin)
    users.append(admin)

    # 일반 유저 19명
    for _ in range(19):
        user = User(
            email=fake.email(),
            password_hash=get_password_hash("password123"),
            name=fake.name(),
            address=fake.address(),
            phone_number=fake.phone_number(),
            gender=random.choice(["MALE", "FEMALE"]),
            role="ROLE_USER"
        )
        db.add(user)
        users.append(user)
    
    db.commit()
    print("✅ 유저 20명 생성 완료")

    # 2. 책 150권 생성
    books = []
    for _ in range(150):
        book = Book(
            title=fake.catch_phrase(),
            authors=fake.name(),
            categories=random.choice(["IT", "소설", "경영", "인문", "과학"]),
            publisher=fake.company(),
            publication_date=fake.date(),
            isbn=fake.isbn13(),
            price=random.randint(10000, 50000),
            description=fake.text(),
            stock_quantity=random.randint(10, 100)
        )
        db.add(book)
        books.append(book)
    
    db.commit()
    # 생성된 책들의 ID를 알기 위해 refresh
    for b in books: db.refresh(b)
    print("✅ 책 150권 생성 완료")

    # 3. 리뷰 50개 생성 (랜덤 유저가 랜덤 책에 리뷰)
    for _ in range(50):
        random_user = random.choice(users)
        random_book = random.choice(books)
        
        review = Review(
            user_id=random_user.id,
            book_id=random_book.id,
            rating=random.randint(1, 5),
            content=fake.sentence()
        )
        db.add(review)
    
    db.commit()
    print("✅ 리뷰 50개 생성 완료")
    
    db.close()
    print("🎉 모든 데이터 시딩이 끝났습니다!")

if __name__ == "__main__":
    seed_data()