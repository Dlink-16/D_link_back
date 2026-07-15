import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import inspect

from app.core.database import get_engine, get_session, init_db
from app.main import app
from app.models.place import ContentType, Place, Region


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("TOURAPI_DB_PATH", str(db_path))
    init_db(str(db_path))

    with get_session(str(db_path)) as session:
        region = Region(code="daejeon", name="대전_충청권")
        content_type = ContentType(content_type_id=12, name="관광지")
        session.add_all([region, content_type])
        session.flush()
        session.add(
            Place(
                region_id=region.id,
                content_type_id=content_type.id,
                external_id="1001",
                title="테스트 장소",
                addr1="대전시",
                addr2="",
                zipcode="12345",
                tel="042-000-0000",
                longitude=127.0,
                latitude=36.0,
                map_level=6,
                area_code="3",
                sigungu_code="1",
                legal_region_code="30",
                legal_sigungu_code="30110",
                cat1="A01",
                cat2="A0101",
                cat3="A01010100",
                classification_l1="VE",
                classification_l2="VE01",
                classification_l3="VE010100",
                copyright_code="Type3",
                first_image="img1",
                first_image2="img2",
                source_file="sample.json",
                created_time="20260101010101",
                modified_time="20260102020202",
            )
        )
        session.add(
            Place(
                region_id=region.id,
                content_type_id=content_type.id,
                external_id="1002",
                title="두 번째 장소",
            )
        )
        session.commit()

    with TestClient(app) as test_client:
        yield test_client


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_place_detail(client):
    response = client.get("/api/places/1")
    assert response.status_code == 200
    payload = response.json()
    assert payload["title"] == "테스트 장소"
    assert payload["addr1"] == "대전시"
    assert payload["legal_region_code"] == "30"
    assert payload["classification_l1"] == "VE"
    assert payload["copyright_code"] == "Type3"


def test_filter_places_by_legal_region(client):
    response = client.get("/api/places/?legal_region_code=30&legal_sigungu_code=30110")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["external_id"] == "1001"


def test_get_missing_place_returns_404(client):
    response = client.get("/api/places/999")

    assert response.status_code == 404


def test_list_places_supports_pagination(client):
    first_page = client.get("/api/places?page=1&limit=1")
    second_page = client.get("/api/places?page=2&limit=1")

    assert first_page.status_code == 200
    assert second_page.status_code == 200
    assert first_page.json()[0]["external_id"] == "1001"
    assert second_page.json()[0]["external_id"] == "1002"


def test_list_places_rejects_invalid_page(client):
    response = client.get("/api/places?page=0")

    assert response.status_code == 422


def test_places_schema_contains_json_fields_and_indexes(client):
    inspector = inspect(get_engine())
    columns = {column["name"] for column in inspector.get_columns("places")}
    indexes = {index["name"] for index in inspector.get_indexes("places")}

    assert {
        "legal_region_code",
        "legal_sigungu_code",
        "classification_l1",
        "classification_l2",
        "classification_l3",
        "copyright_code",
    } <= columns
    assert "idx_places_external_id" in indexes
    assert "idx_places_region_type_id" in indexes
    assert "idx_places_legal_region_sigungu_id" in indexes
