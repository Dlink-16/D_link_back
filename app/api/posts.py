"""익명 커뮤니티 게시글 CRUD API를 제공한다."""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.models.place import ContentType
from app.models.post import Post
from app.schemas.post import DeleteResponse, PostCreate, PostResponse, PostUpdate

router = APIRouter(prefix="/api/posts", tags=["posts"])


def get_kst_now() -> str:
    """현재 시간을 한국 표준시(KST) 문자열로 반환한다."""
    return (datetime.now(timezone.utc) + timedelta(hours=9)).strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def serialize_post(post: Post) -> dict:
    """평문 비밀번호를 제외하고 외부에 공개할 게시글 필드만 직렬화한다."""
    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "category": post.category,
        "created_at": post.created_at,
        "updated_at": post.updated_at,
    }


def validate_category(category: str, session: Session) -> None:
    """카테고리가 제공 데이터의 콘텐츠 유형에 포함되는지 확인한다."""
    content_type = session.scalar(
        select(ContentType).where(ContentType.name == category)
    )
    if content_type is None:
        raise HTTPException(status_code=422, detail="invalid category")


@router.get("/", response_model=list[PostResponse])
def list_posts(
    category: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    session: Session = Depends(get_db_session),
):
    """최신 게시글을 카테고리 선택 조건과 함께 조회한다."""
    statement = select(Post)
    if category:
        statement = statement.where(Post.category == category)
    offset = (page - 1) * limit
    posts = session.scalars(
        statement.order_by(Post.id.desc()).offset(offset).limit(limit)
    ).all()
    return [serialize_post(post) for post in posts]


@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: int, session: Session = Depends(get_db_session)):
    """게시글 한 건을 조회하고 없으면 404를 반환한다."""
    post = session.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="post not found")
    return serialize_post(post)


@router.post("/", status_code=201, response_model=PostResponse)
def create_post(payload: PostCreate, session: Session = Depends(get_db_session)):
    """수정용 비밀번호를 포함한 익명 게시글을 저장한다."""
    # 게시글과 콘텐츠 유형 사이에 외래키는 두지 않고 생성 시 이름만 검증한다.
    validate_category(payload.category, session)
    post_data = payload.model_dump()
    post_data["created_at"] = get_kst_now()
    post_data["updated_at"] = get_kst_now()
    post = Post(**post_data)
    session.add(post)
    session.commit()
    session.refresh(post)
    return serialize_post(post)


@router.put("/{post_id}", response_model=PostResponse)
def update_post(
    post_id: int,
    payload: PostUpdate,
    session: Session = Depends(get_db_session),
):
    """등록된 비밀번호가 일치할 때 게시글 내용을 수정한다."""
    post = session.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="post not found")
    if post.password != payload.password:
        raise HTTPException(status_code=403, detail="password mismatch")

    if payload.title is not None:
        post.title = payload.title
    if payload.content is not None:
        post.content = payload.content
    post.updated_at = get_kst_now()

    session.commit()
    session.refresh(post)
    return serialize_post(post)


@router.delete("/{post_id}", response_model=DeleteResponse)
def delete_post(
    post_id: int,
    password: str,
    session: Session = Depends(get_db_session),
):
    """등록된 비밀번호가 일치할 때 게시글을 삭제한다."""
    post = session.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="post not found")
    if post.password != password:
        raise HTTPException(status_code=403, detail="password mismatch")

    session.delete(post)
    session.commit()
    return {"deleted": True}
