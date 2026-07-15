"""관광 데이터의 권역, 콘텐츠 유형, 장소 ORM 모델을 정의한다."""

from typing import Optional

from sqlalchemy import Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Region(Base):
    """제공 데이터가 속한 권역."""

    __tablename__ = "regions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)

    places: Mapped[list["Place"]] = relationship(back_populates="region")


class ContentType(Base):
    """관광지·음식점 등 제공 JSON의 콘텐츠 유형."""

    __tablename__ = "content_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    content_type_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)

    places: Mapped[list["Place"]] = relationship(back_populates="content_type")


class Place(Base):
    """제공 JSON에서 적재한 관광 장소와 원본 메타데이터."""

    __tablename__ = "places"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    region_id: Mapped[int] = mapped_column(ForeignKey("regions.id"), nullable=False)
    content_type_id: Mapped[int] = mapped_column(ForeignKey("content_types.id"), nullable=False)
    external_id: Mapped[str] = mapped_column(String, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    addr1: Mapped[Optional[str]] = mapped_column(Text)
    addr2: Mapped[Optional[str]] = mapped_column(Text)
    zipcode: Mapped[Optional[str]] = mapped_column(String)
    tel: Mapped[Optional[str]] = mapped_column(String)
    longitude: Mapped[Optional[float]] = mapped_column(Float)
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    map_level: Mapped[Optional[int]] = mapped_column(Integer)
    area_code: Mapped[Optional[str]] = mapped_column(String)
    sigungu_code: Mapped[Optional[str]] = mapped_column(String)
    legal_region_code: Mapped[Optional[str]] = mapped_column(String)
    legal_sigungu_code: Mapped[Optional[str]] = mapped_column(String)
    cat1: Mapped[Optional[str]] = mapped_column(String)
    cat2: Mapped[Optional[str]] = mapped_column(String)
    cat3: Mapped[Optional[str]] = mapped_column(String)
    classification_l1: Mapped[Optional[str]] = mapped_column(String)
    classification_l2: Mapped[Optional[str]] = mapped_column(String)
    classification_l3: Mapped[Optional[str]] = mapped_column(String)
    copyright_code: Mapped[Optional[str]] = mapped_column(String)
    first_image: Mapped[Optional[str]] = mapped_column(Text)
    first_image2: Mapped[Optional[str]] = mapped_column(Text)
    source_file: Mapped[Optional[str]] = mapped_column(String)
    created_time: Mapped[Optional[str]] = mapped_column(String)
    modified_time: Mapped[Optional[str]] = mapped_column(String)

    region: Mapped[Region] = relationship(back_populates="places")
    content_type: Mapped[ContentType] = relationship(back_populates="places")

    __table_args__ = (
        Index("idx_places_external_id", "external_id", unique=True),
        Index("idx_places_region", "region_id"),
        Index("idx_places_content_type", "content_type_id"),
        Index("idx_places_region_type_id", "region_id", "content_type_id", "id"),
        Index(
            "idx_places_legal_region_sigungu_id",
            "legal_region_code",
            "legal_sigungu_code",
            "id",
        ),
    )
