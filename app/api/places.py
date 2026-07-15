"""관광 장소 목록과 상세 조회 API를 제공한다."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.models.place import ContentType, Place, Region
from app.schemas.place import PlaceDetailResponse, PlaceListResponse

router = APIRouter(prefix="/api/places", tags=["places"])


@router.get("/", response_model=list[PlaceListResponse])
def list_places(
    region: str | None = Query(default=None),
    content_type: str | None = Query(default=None),
    legal_region_code: str | None = Query(default=None),
    legal_sigungu_code: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    session: Session = Depends(get_db_session),
):
    """선택 조건으로 관광 장소를 필터링해 최대 100건 반환한다."""
    statement = (
        select(
            Place.id,
            Place.external_id,
            Place.title,
            Place.addr1,
            Place.latitude,
            Place.longitude,
            Place.legal_region_code,
            Place.legal_sigungu_code,
            Place.classification_l1,
            Place.classification_l2,
            Place.classification_l3,
            Place.first_image,
            Place.copyright_code,
            Region.name.label("region_name"),
            ContentType.name.label("content_type_name"),
        )
        .join(Region, Place.region_id == Region.id)
        .join(ContentType, Place.content_type_id == ContentType.id)
    )

    if region:
        statement = statement.where(Region.code == region)
    if content_type:
        statement = statement.where(ContentType.name == content_type)
    if legal_region_code:
        statement = statement.where(Place.legal_region_code == legal_region_code)
    if legal_sigungu_code:
        statement = statement.where(Place.legal_sigungu_code == legal_sigungu_code)

    offset = (page - 1) * limit
    rows = (
        session.execute(statement.order_by(Place.id).offset(offset).limit(limit))
        .mappings()
        .all()
    )
    return [dict(row) for row in rows]


@router.get("/{place_id}", response_model=PlaceDetailResponse)
def get_place(place_id: int, session: Session = Depends(get_db_session)):
    """장소 한 건의 원본 메타데이터와 분류 정보를 반환한다."""
    statement = (
        select(
            Place.id,
            Place.external_id,
            Place.title,
            Place.addr1,
            Place.addr2,
            Place.zipcode,
            Place.tel,
            Place.longitude,
            Place.latitude,
            Place.map_level,
            Place.area_code,
            Place.sigungu_code,
            Place.legal_region_code,
            Place.legal_sigungu_code,
            Place.cat1,
            Place.cat2,
            Place.cat3,
            Place.classification_l1,
            Place.classification_l2,
            Place.classification_l3,
            Place.copyright_code,
            Place.first_image,
            Place.first_image2,
            Place.source_file,
            Place.created_time,
            Place.modified_time,
            Region.name.label("region_name"),
            ContentType.name.label("content_type_name"),
        )
        .join(Region, Place.region_id == Region.id)
        .join(ContentType, Place.content_type_id == ContentType.id)
        .where(Place.id == place_id)
    )
    row = session.execute(statement).mappings().one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="place not found")
    return dict(row)
