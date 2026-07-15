"""제공 JSON을 기반으로 적재된 게시판 카테고리 조회 API를 제공한다."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.models.place import ContentType
from app.schemas.content_type import ContentTypeResponse


router = APIRouter(prefix="/api/content-types", tags=["content-types"])


@router.get("/", response_model=list[ContentTypeResponse])
def list_content_types(
    session: Session = Depends(get_db_session),
) -> list[ContentTypeResponse]:
    """게시글 작성에 사용할 수 있는 콘텐츠 유형을 반환한다."""
    content_types = session.scalars(
        select(ContentType).order_by(ContentType.content_type_id)
    ).all()
    return [
        {
            "content_type_id": content_type.content_type_id,
            "name": content_type.name,
        }
        for content_type in content_types
    ]
