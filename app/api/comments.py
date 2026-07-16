"""게시글별 익명 댓글 CRUD API를 제공한다."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.posts import get_kst_now
from app.core.database import get_db_session
from app.models.comment import Comment
from app.models.post import Post
from app.schemas.comment import (
    CommentCreate,
    CommentDeleteResponse,
    CommentResponse,
    CommentUpdate,
)
from app.schemas.post import PasswordVerify, PasswordVerifyResponse

router = APIRouter(prefix="/api/posts", tags=["comments"])


def get_comment(post_id: int, comment_id: int, session: Session) -> Comment:
    comment = session.scalar(
        select(Comment).where(
            Comment.id == comment_id,
            Comment.post_id == post_id,
        )
    )
    if comment is None:
        raise HTTPException(status_code=404, detail="comment not found")
    return comment


def serialize_comment(comment: Comment) -> dict:
    return {
        "id": comment.id,
        "post_id": comment.post_id,
        "content": comment.content,
        "created_at": comment.created_at,
        "updated_at": comment.updated_at,
    }


@router.get("/{post_id}/comments", response_model=list[CommentResponse])
def list_comments(post_id: int, session: Session = Depends(get_db_session)):
    if session.get(Post, post_id) is None:
        raise HTTPException(status_code=404, detail="post not found")
    comments = session.scalars(
        select(Comment)
        .where(Comment.post_id == post_id)
        .order_by(Comment.id.desc())
    ).all()
    return [serialize_comment(comment) for comment in comments]


@router.post(
    "/{post_id}/comments", status_code=201, response_model=CommentResponse
)
def create_comment(
    post_id: int,
    payload: CommentCreate,
    session: Session = Depends(get_db_session),
):
    if session.get(Post, post_id) is None:
        raise HTTPException(status_code=404, detail="post not found")
    now = get_kst_now()
    comment = Comment(
        post_id=post_id,
        content=payload.content,
        password=payload.password,
        created_at=now,
        updated_at=now,
    )
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return serialize_comment(comment)


@router.post(
    "/{post_id}/comments/{comment_id}/verify-password",
    response_model=PasswordVerifyResponse,
)
def verify_comment_password(
    post_id: int,
    comment_id: int,
    payload: PasswordVerify,
    session: Session = Depends(get_db_session),
):
    comment = get_comment(post_id, comment_id, session)
    if comment.password != payload.password:
        raise HTTPException(status_code=403, detail="password mismatch")
    return {"valid": True}


@router.put(
    "/{post_id}/comments/{comment_id}", response_model=CommentResponse
)
def update_comment(
    post_id: int,
    comment_id: int,
    payload: CommentUpdate,
    session: Session = Depends(get_db_session),
):
    comment = get_comment(post_id, comment_id, session)
    if comment.password != payload.password:
        raise HTTPException(status_code=403, detail="password mismatch")
    comment.content = payload.content
    comment.updated_at = get_kst_now()
    session.commit()
    session.refresh(comment)
    return serialize_comment(comment)


@router.delete(
    "/{post_id}/comments/{comment_id}", response_model=CommentDeleteResponse
)
def delete_comment(
    post_id: int,
    comment_id: int,
    password: str,
    session: Session = Depends(get_db_session),
):
    comment = get_comment(post_id, comment_id, session)
    if comment.password != password:
        raise HTTPException(status_code=403, detail="password mismatch")
    session.delete(comment)
    session.commit()
    return {"deleted": True}
