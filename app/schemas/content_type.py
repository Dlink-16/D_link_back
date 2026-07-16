"""콘텐츠 유형 API의 응답 스키마를 정의한다."""

from pydantic import BaseModel


class ContentTypeResponse(BaseModel):
    """게시글 카테고리로 사용할 콘텐츠 유형 응답."""

    content_type_id: int
    name: str
