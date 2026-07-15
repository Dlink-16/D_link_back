"""게시글 생성과 수정 요청의 입력값 스키마를 정의한다."""

from pydantic import BaseModel, Field


class PostCreate(BaseModel):
    """새 게시글 작성 시 필요한 입력값."""

    title: str = Field(min_length=1)
    content: str = Field(min_length=1)
    password: str = Field(min_length=1)
    category: str = Field(min_length=1)


class PostUpdate(BaseModel):
    """게시글 수정 시 필요한 비밀번호와 선택 입력값."""

    title: str | None = Field(default=None, min_length=1)
    content: str | None = Field(default=None, min_length=1)
    password: str = Field(min_length=1)


class PostResponse(BaseModel):
    """평문 비밀번호를 제외한 게시글 응답."""

    id: int
    title: str
    content: str
    category: str
    created_at: str
    updated_at: str


class PostCountResponse(BaseModel):
    """게시글 목록 조건에 맞는 전체 게시글 수 응답."""

    total: int


class DeleteResponse(BaseModel):
    """게시글 삭제 결과 응답."""

    deleted: bool
