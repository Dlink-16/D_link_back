"""제공 JSON 관광 데이터를 SQLite에 반복 적재할 수 있게 변환한다."""

import json
from pathlib import Path

from sqlalchemy import select

from app.core.database import get_session, init_db
from app.models.place import ContentType, Place, Region


RAW_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "raw"


def load_region_code(region_name: str) -> str:
    """파일의 권역명을 URL 및 조회 조건에 사용할 코드로 정규화한다."""
    return region_name.replace("_", "-")


def _to_optional_float(value: object) -> float | None:
    """비어 있는 JSON 값을 None으로 보존하며 실수로 변환한다."""
    if value in (None, ""):
        return None
    return float(value)


def _to_optional_int(value: object) -> int | None:
    """비어 있는 JSON 값을 None으로 보존하며 정수로 변환한다."""
    if value in (None, ""):
        return None
    return int(value)


def _place_values(item: dict, source_file: str) -> dict:
    """JSON 장소 필드를 Place 모델에 저장할 값으로 변환한다."""
    longitude = _to_optional_float(item.get("mapx"))
    latitude = _to_optional_float(item.get("mapy"))
    # 원본의 (0, 0)은 실제 좌표가 아니라 좌표 정보 없음으로 취급한다.
    if longitude == 0.0 and latitude == 0.0:
        longitude = None
        latitude = None

    return {
        "title": item.get("title", ""),
        "addr1": item.get("addr1", ""),
        "addr2": item.get("addr2", ""),
        "zipcode": item.get("zipcode", ""),
        "tel": item.get("tel", ""),
        "longitude": longitude,
        "latitude": latitude,
        "map_level": _to_optional_int(item.get("mlevel")),
        "area_code": item.get("areacode", ""),
        "sigungu_code": item.get("sigungucode", ""),
        "legal_region_code": item.get("lDongRegnCd", ""),
        "legal_sigungu_code": item.get("lDongSignguCd", ""),
        "cat1": item.get("cat1", ""),
        "cat2": item.get("cat2", ""),
        "cat3": item.get("cat3", ""),
        "classification_l1": item.get("lclsSystm1", ""),
        "classification_l2": item.get("lclsSystm2", ""),
        "classification_l3": item.get("lclsSystm3", ""),
        "copyright_code": item.get("cpyrhtDivCd", ""),
        "first_image": item.get("firstimage", ""),
        "first_image2": item.get("firstimage2", ""),
        "source_file": source_file,
        "created_time": item.get("createdtime", ""),
        "modified_time": item.get("modifiedtime", ""),
    }


def import_json_files(data_dir: Path | None = None) -> int:
    """JSON 파일을 신규 생성 또는 갱신하고 처리한 장소 수를 반환한다."""
    init_db()
    data_dir = data_dir or RAW_DATA_DIR

    with get_session() as session:
        region_name = "대전_충청권"
        region_code = load_region_code(region_name)
        region = session.scalar(select(Region).where(Region.code == region_code))
        if region is None:
            region = Region(code=region_code, name=region_name)
            session.add(region)
            session.flush()
        else:
            region.name = region_name

        # 기존 행을 먼저 읽어 동일 데이터를 재실행해도 중복되지 않게 갱신한다.
        content_types = {
            content_type.content_type_id: content_type
            for content_type in session.scalars(select(ContentType)).all()
        }
        places = {
            place.external_id: place
            for place in session.scalars(select(Place)).all()
        }

        processed_count = 0
        for json_path in sorted(data_dir.glob("*.json")):
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            external_content_type_id = int(payload.get("contentTypeId", 0))
            content_type_name = payload.get("contentType", "")

            content_type = content_types.get(external_content_type_id)
            if content_type is None:
                content_type = ContentType(
                    content_type_id=external_content_type_id,
                    name=content_type_name,
                )
                session.add(content_type)
                session.flush()
                content_types[external_content_type_id] = content_type
            else:
                content_type.name = content_type_name

            for item in payload.get("items", []):
                external_id = str(item.get("contentid", ""))
                values = _place_values(item, json_path.name)
                place = places.get(external_id)

                if place is None:
                    place = Place(
                        region_id=region.id,
                        content_type_id=content_type.id,
                        external_id=external_id,
                        **values,
                    )
                    session.add(place)
                    places[external_id] = place
                else:
                    place.region_id = region.id
                    place.content_type_id = content_type.id
                    for field, value in values.items():
                        setattr(place, field, value)

                processed_count += 1

        session.commit()
        return processed_count


if __name__ == "__main__":
    imported_count = import_json_files()
    print(f"Imported {imported_count} places.")
