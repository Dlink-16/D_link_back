# LocalHub - 지역 정보 공유 커뮤니티 백엔드

**프로젝트**: LocalHub (공공데이터 기반 지역 정보 공유 커뮤니티)  
**기술 스택**: FastAPI + SQLite + SQLAlchemy ORM  
**개발 기한**: 2026.7.14 ~ 2026.7.16  
**배포**: Render  

---

## 📋 프로젝트 개요

### 필수 기능 요구사항

#### 1. 커뮤니티 기능 (CRUD)
- ✅ **익명 커뮤니티**: 회원가입/로그인 없음
- ✅ **비밀번호 기반 권한**: 게시글 작성 시 비밀번호 등록 → 수정/삭제 시 비밀번호 확인
- ✅ **⚠️ 비밀번호는 평문으로 저장** (교육 목적, 의도된 설계)
- ✅ **카테고리 게시판**: 선정한 1개 권역의 카테고리별 게시판
- ✅ **필수 API**: 목록, 상세, 작성, 수정, 삭제

#### 2. 챗봇 기능
- ✅ **엔드포인트**: `POST /api/chat`
- ✅ **기술**: OpenAI API 활용 (제공된 API 키 사용)
- ✅ **기능**: 제공 JSON 데이터 기반 자연어 질의응답
- ✅ **주요 질의 유형**:
  - 권역별 관광지 추천
  - 축제 일정 안내
  - 모범음식점 위치
  - 커뮤니티 게시글 검색
  - 기타 지역 정보

#### 3. 환경 변수 관리
- ✅ `.env` 파일 사용
- ✅ API 키, DB 경로 등 **절대 GitHub에 올리지 않음**
- ✅ `.gitignore`에 `.env` 등록

#### 4. 데이터베이스
- ✅ **SQLite** (별도 DB 서버 불필요)
- ✅ **SQLAlchemy ORM** 사용
- ✅ 커뮤니티 데이터 반드시 DB에 저장

---

## 📁 프로젝트 구조

```
D.link-back/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI 앱 진입점
│   │
│   ├── api/                       # API 라우터
│   │   ├── __init__.py
│   │   ├── posts.py               # 게시글 CRUD 엔드포인트 구현 필요
│   │   └── chat.py                # 챗봇 엔드포인트 구현 필요
│   │
│   ├── core/                      # 설정, 데이터베이스
│   │   ├── __init__.py
│   │   ├── config.py              # 환경변수 관리
│   │   └── database.py            # SQLite 연결 설정
│   │
│   ├── models/                    # SQLAlchemy ORM 모델
│   │   ├── __init__.py
│   │   └── post.py                # Post 모델 정의 필요
│   │
│   ├── schemas/                   # Pydantic 스키마
│   │   ├── __init__.py
│   │   └── post.py                # PostCreate, PostUpdate 등 정의 필요
│   │
│   └── services/                  # 비즈니스 로직
│       ├── __init__.py
│       ├── post_service.py         # 게시글 CRUD 로직 구현 필요
│       └── chat_service.py         # 챗봇 로직 구현 필요
│
├── data/                          # 공공데이터 JSON 파일
│   ├── seoul.json
│   ├── daejeon.json
│   ├── gumi.json
│   ├── gwangju.json
│   └── busan.json
│
├── requirements.txt               # 패키지 의존성
├── .env.example                   # 환경변수 템플릿
├── .gitignore                     # Git 제외 파일
├── Procfile                       # Render 배포 설정
├── runtime.txt                    # Python 버전 명시
└── README.md
```

---

## 🚀 설치 및 실행

### 1. 가상환경 활성화
```bash
# 이미 생성된 data_pj 가상환경 사용
cd ../data_pj

# Windows
Scripts/activate

# macOS/Linux
source bin/activate
```

### 2. 패키지 설치
```bash
cd ../D.link-back
pip install -r requirements.txt
```

### 3. 환경 변수 설정
```bash
# .env.example을 .env로 복사
cp .env.example .env

# 다음 항목 필수 입력:
# - OPENAI_API_KEY: sk-... (챗봇용)
# - REGION: seoul (선택한 권역)
# - DATABASE_URL: sqlite:///./localhub.db (기본값 사용 가능)
```

### 4. 데이터베이스 초기화
```bash
# main.py 실행 시 자동 초기화됨
# 또는 수동 초기화:
python -c "from app.core.database import init_db; init_db()"
```

### 5. 서버 실행
```bash
# 개발 모드 (자동 리로드)
uvicorn app.main:app --reload

# 또는
python app/main.py
```

**서버 실행 확인**: http://localhost:8000

---

## 📚 API 명세

### Swagger UI 및 ReDoc
```
http://localhost:8000/docs          # Swagger UI
http://localhost:8000/redoc         # ReDoc (대안 문서)
```

### 필수 엔드포인트

#### 게시글 CRUD API

| 메서드 | 경로 | 기능 | 입력 |
|--------|------|------|------|
| **GET** | `/api/posts` | 게시글 목록 조회 | `category`, `page`, `limit` |
| **GET** | `/api/posts/{post_id}` | 게시글 상세 조회 | - |
| **POST** | `/api/posts` | 게시글 작성 | `title`, `content`, `password`, `category` |
| **PUT** | `/api/posts/{post_id}` | 게시글 수정 | `title`, `content`, `password` |
| **DELETE** | `/api/posts/{post_id}` | 게시글 삭제 | `password` (Query 파라미터) |

**게시글 작성 요청 예시**:
```json
{
  "title": "강남역 추천 카페",
  "content": "조용하고 분위기 좋은 카페입니다...",
  "password": "1234",
  "category": "카페"
}
```

**게시글 응답 예시**:
```json
{
  "id": 1,
  "title": "강남역 추천 카페",
  "content": "조용하고 분위기 좋은 카페입니다...",
  "category": "카페",
  "created_at": "2026-07-14T10:30:00",
  "updated_at": "2026-07-14T10:30:00"
}
```

#### 챗봇 API

| 메서드 | 경로 | 기능 |
|--------|------|------|
| **POST** | `/api/chat` | 자연어 질의응답 |

**요청**:
```json
{
  "message": "서울의 유명한 관광지를 추천해줄래?",
  "region": "seoul"
}
```

**응답**:
```json
{
  "response": "서울의 주요 관광지는 다음과 같습니다: 남대문시장, 명동, 종로...",
  "sources": ["공공데이터"],
  "region": "seoul"
}
```

---

## ⚙️ 환경 변수 (.env)

```env
# 서버 설정
ENV=development
API_HOST=0.0.0.0
API_PORT=8000

# 데이터베이스
DATABASE_URL=sqlite:///./localhub.db

# OpenAI API (필수 - 챗봇)
OPENAI_API_KEY=sk-your-api-key-here

# CORS 설정 (프론트엔드 URL)
CORS_ORIGINS=["http://localhost:3000"]

# 선택한 권역
REGION=seoul  # seoul, daejeon, gumi, gwangju, busan
```

---

## 🔧 개발 가이드

### 데이터베이스 스키마

#### posts 테이블 (필수)
```sql
CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    password VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 구현 순서 (권장)

#### Phase 1: 게시글 기능
1. **`app/models/post.py`**: Post 모델 정의
2. **`app/schemas/post.py`**: PostCreate, PostUpdate, PostResponse 스키마 정의
3. **`app/services/post_service.py`**: 게시글 CRUD 비즈니스 로직
4. **`app/api/posts.py`**: FastAPI 라우터 구현
5. **`app/main.py`**: 라우터 등록

#### Phase 2: 챗봇 기능
1. **`app/services/chat_service.py`**: OpenAI API 통합
2. **`app/api/chat.py`**: 챗봇 엔드포인트

### 코딩 컨벤션

**파일명**: `snake_case`  
```python
post_service.py, post_router.py
```

**클래스명**: `PascalCase`  
```python
class PostService:
class PostCreate(BaseModel):
```

**함수명**: `snake_case`  
```python
def get_all_posts():
def create_post():
```

### 새 라우터 추가 방법

1. `app/api/` 에 `{기능}.py` 파일 생성
2. APIRouter 정의
3. `app/main.py`에 `app.include_router()` 등록

```python
# app/main.py
from app.api import posts, chat

app.include_router(posts.router)
app.include_router(chat.router)
```

---

## ⚠️ 주의사항

### 필수 확인 사항

1. **비밀번호 평문 저장**
   - ❌ 실제 프로덕션에서는 암호화 필수
   - ✅ 이 프로젝트는 교육용 (의도된 설계)

2. **.env 파일 관리**
   - ❌ GitHub에 절대 올리지 않음
   - ✅ `.gitignore`에 `.env` 등록 확인

3. **API 키 보안**
   - ❌ 소스 코드에 하드코딩 금지
   - ✅ 환경변수로만 관리

4. **CORS 설정**
   - 프론트엔드 URL과 반드시 일치
   - 개발 환경: `http://localhost:3000` 또는 `http://localhost:5173`

5. **SQLite 파일 관리**
   - `.gitignore`에 `.db` 파일 등록
   - 프로덕션에서는 초기 데이터 포함된 `.db` 파일 제공

---

## 🚢 배포 가이드 (Render)

### 사전 준비
1. GitHub에 저장소 푸시 (.env 파일 제외 확인)
2. Render.com 회원가입

### 배포 절차
1. Render → "New +" → "Web Service"
2. GitHub 저장소 선택
3. 다음 설정 입력:
   - **Build command**: `pip install -r requirements.txt`
   - **Start command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. 환경 변수 설정:
   - `OPENAI_API_KEY`: sk-...
   - `REGION`: seoul
   - 기타 필요한 환경변수

5. Deploy!

### 배포 후 확인
- 배포된 URL 접속 확인
- `/health` 엔드포인트로 상태 확인
- Swagger UI (`/docs`)로 API 확인

---

## 📝 공공데이터 활용

### 제공 데이터 현황

각 권역별로 다음 데이터 제공:
- 관광지
- 문화시설
- 축제공연행사
- 여행 코스
- 레포츠
- 숙박
- 쇼핑
- 음식점

### 데이터 폴더 구조

```
data/
├── seoul.json         # 서울 데이터
├── daejeon.json       # 대전/충청 데이터
├── gumi.json          # 구미/경북 데이터
├── gwangju.json       # 광주/전라 데이터
└── busan.json         # 부산 데이터
```

### 라이선스 확인
- ✅ 제공 JSON 데이터는 사용 가능
- ⚠️ 추가 수집 시 **라이선스 사전 확인** (공공누리 유형 1~4 확인)
- 기능 명세서에 데이터 출처·라이선스 기록 필수

---

## 🐛 트러블슈팅

### 데이터베이스 에러
```bash
# DB 초기화
python -c "from app.core.database import init_db; init_db()"
```

### OpenAI API 연결 실패
- `.env`에 유효한 `OPENAI_API_KEY` 확인
- API 사용량 및 잔액 확인

### CORS 에러
- `.env`의 `CORS_ORIGINS`와 프론트 URL 일치 확인
- 브라우저 콘솔의 CORS 에러 메시지 확인

### 모듈 임포트 에러
- `pip install -r requirements.txt` 재실행
- Python 경로 확인

---

## 📅 개발 마일스톤

- **Day 1 (7/14)**: 프로젝트 초기화, 폴더 구조 설계
- **Day 2 (7/15)**: 게시글 CRUD, 챗봇 기능 구현 및 테스트
- **Day 3 (7/16)**: 최종 테스트, 배포, 문서화 (납기: 15:00)

---

## 📚 참고 자료

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Pydantic 문서](https://docs.pydantic.dev/)
- [OpenAI API 문서](https://platform.openai.com/docs/api-reference)
- [Render 배포 가이드](https://render.com/docs)
