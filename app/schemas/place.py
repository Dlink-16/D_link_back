"""관광 장소 목록과 상세 API의 응답 스키마를 정의한다."""

from pydantic import BaseModel


class PlaceListResponse(BaseModel):
    """관광 장소 목록에서 제공하는 요약 정보."""

    id: int
    external_id: str
    title: str
    addr1: str | None
    latitude: float | None
    longitude: float | None
    legal_region_code: str | None
    legal_sigungu_code: str | None
    classification_l1: str | None
    classification_l2: str | None
    classification_l3: str | None
    first_image: str | None
    copyright_code: str | None
    region_name: str
    content_type_name: str


class PlaceCountResponse(BaseModel):
    """장소 목록 조건에 맞는 전체 장소 수 응답."""

    total: int


class PlaceDetailResponse(PlaceListResponse):
    """관광 장소 한 건의 전체 원본 메타데이터."""

    addr2: str | None
    zipcode: str | None
    tel: str | None
    map_level: int | None
    area_code: str | None
    sigungu_code: str | None
    cat1: str | None
    cat2: str | None
    cat3: str | None
    first_image2: str | None
    source_file: str | None
    created_time: str | None
    modified_time: str | None
