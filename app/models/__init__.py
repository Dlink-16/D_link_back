"""테이블 생성 시 등록할 ORM 모델을 한곳에서 공개한다."""

from app.models.base import Base
from app.models.comment import Comment
from app.models.place import ContentType, Place, Region
from app.models.post import Post

__all__ = ["Base", "Comment", "ContentType", "Place", "Post", "Region"]
