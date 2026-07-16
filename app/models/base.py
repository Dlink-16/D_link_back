"""모든 SQLAlchemy ORM 모델이 상속할 선언형 베이스를 제공한다."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """프로젝트 ORM 모델의 공통 선언형 베이스."""

    pass
