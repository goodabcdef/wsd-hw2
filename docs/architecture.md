# 🏗️ 시스템 아키텍처 (Architecture)

## 1. 기술 스택
- **Language**: Python 3.10+
- **Web Framework**: FastAPI
- **Database**: MySQL (Production), SQLite (Dev)
- **ORM**: SQLAlchemy
- **Server**: Uvicorn (ASGI), PM2 (Process Manager)

## 2. 폴더 구조 (Layered Architecture)
관심사 분리 원칙에 따라 계층을 나누어 설계했습니다.

- **app/api**: 컨트롤러 계층 (Router). 요청을 받아 Service/DB 로직을 호출하고 응답을 반환.
- **app/schemas**: DTO (Data Transfer Object). Pydantic을 사용한 요청/응답 데이터 검증.
- **app/models**: Entity 계층. 데이터베이스 테이블 정의 (SQLAlchemy).
- **app/db**: 데이터베이스 연결 세션 관리.
- **app/core**: 설정(Config), 보안(Security/JWT) 등 공통 모듈.

## 3. 배포 아키텍처
- **Process Manager**: PM2를 사용하여 무중단 서비스 및 자동 재시작 구현.
- **Reverse Proxy**: (선택 사항) Nginx 등을 앞단에 배치 가능.