import json

from sqlalchemy import func, select

from app.core.database import get_session
from app.models.place import Place
from app.services.data_loader import import_json_files


def test_import_json_preserves_metadata_and_updates_existing_row(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    db_path = tmp_path / "tourapi.db"
    monkeypatch.setenv("TOURAPI_DB_PATH", str(db_path))

    item = {
        "contentid": "1001",
        "contenttypeid": "12",
        "title": "테스트 장소",
        "addr1": "",
        "addr2": "",
        "zipcode": "",
        "tel": "",
        "mapx": "0",
        "mapy": "0",
        "mlevel": "6",
        "areacode": "",
        "sigungucode": "",
        "lDongRegnCd": "30",
        "lDongSignguCd": "30110",
        "cat1": "A01",
        "cat2": "A0101",
        "cat3": "A01010100",
        "lclsSystm1": "VE",
        "lclsSystm2": "VE01",
        "lclsSystm3": "VE010100",
        "firstimage": "https://example.com/image.jpg",
        "firstimage2": "https://example.com/thumb.jpg",
        "cpyrhtDivCd": "Type3",
        "createdtime": "20260101010101",
        "modifiedtime": "20260102020202",
    }
    payload = {
        "region": "대전_충청권",
        "contentType": "관광지",
        "contentTypeId": 12,
        "total": 1,
        "items": [item],
    }
    json_path = data_dir / "sample.json"
    json_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    assert import_json_files(data_dir) == 1

    with get_session() as session:
        place = session.scalar(select(Place).where(Place.external_id == "1001"))
        assert place is not None
        assert place.longitude is None
        assert place.latitude is None
        assert place.legal_region_code == "30"
        assert place.classification_l3 == "VE010100"
        assert place.copyright_code == "Type3"

    payload["items"][0]["title"] = "수정된 장소"
    json_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    assert import_json_files(data_dir) == 1

    with get_session() as session:
        assert session.scalar(select(func.count()).select_from(Place)) == 1
        assert session.scalar(select(Place.title)) == "수정된 장소"
