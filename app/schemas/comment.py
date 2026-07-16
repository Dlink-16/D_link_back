"""댓글 생성·수정 요청과 응답 스키마를 정의한다."""

from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    content: str = Field(min_length=1)
    password: str = Field(min_length=1)


class CommentUpdate(BaseModel):
    content: str = Field(min_length=1)
    password: str = Field(min_length=1)


class CommentResponse(BaseModel):
    id: int
    post_id: int
    content: str
    created_at: str
    updated_at: str


class CommentDeleteResponse(BaseModel):
    deleted: bool
