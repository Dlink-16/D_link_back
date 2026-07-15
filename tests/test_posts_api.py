import pytest
from fastapi.testclient import TestClient

from app.core.database import init_db
from app.core.database import get_session
from app.main import app
from app.models.place import ContentType


CONTENT_TYPES = [
    (12, "관광지"),
    (14, "문화시설"),
    (15, "축제공연행사"),
    (25, "여행코스"),
    (28, "레포츠"),
    (32, "숙박"),
    (38, "쇼핑"),
    (39, "음식점"),
]


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "test_posts.db"
    monkeypatch.setenv("TOURAPI_DB_PATH", str(db_path))
    init_db(str(db_path))

    with get_session(str(db_path)) as session:
        session.add_all(
            [
                ContentType(content_type_id=content_type_id, name=name)
                for content_type_id, name in CONTENT_TYPES
            ]
        )
        session.commit()

    with TestClient(app) as test_client:
        yield test_client


def test_create_and_get_post(client):
    response = client.post(
        "/api/posts",
        json={
            "title": "테스트 글",
            "content": "테스트 본문",
            "password": "1234",
            "category": "관광지",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["title"] == "테스트 글"
    assert payload["category"] == "관광지"
    assert "password" not in payload

    detail_response = client.get(f"/api/posts/{payload['id']}")
    assert detail_response.status_code == 200
    assert detail_response.json()["content"] == "테스트 본문"


def test_update_and_delete_post(client):
    create_response = client.post(
        "/api/posts",
        json={
            "title": "원본 제목",
            "content": "원본 본문",
            "password": "1234",
            "category": "음식점",
        },
    )
    post_id = create_response.json()["id"]

    update_response = client.put(
        f"/api/posts/{post_id}",
        json={
            "title": "수정 제목",
            "content": "수정 본문",
            "password": "1234",
        },
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "수정 제목"

    delete_response = client.delete(f"/api/posts/{post_id}?password=1234")
    assert delete_response.status_code == 200
    assert delete_response.json()["deleted"] is True


def test_list_content_types(client):
    response = client.get("/api/content-types")

    assert response.status_code == 200
    assert response.json() == [
        {"content_type_id": content_type_id, "name": name}
        for content_type_id, name in CONTENT_TYPES
    ]


def test_create_post_rejects_unknown_category(client):
    response = client.post(
        "/api/posts",
        json={
            "title": "잘못된 카테고리",
            "content": "본문",
            "password": "1234",
            "category": "카페",
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "invalid category"


def test_wrong_password_cannot_update_or_delete(client):
    post_id = _create_post(client, title="비밀번호 확인")["id"]

    update_response = client.put(
        f"/api/posts/{post_id}",
        json={"title": "수정 시도", "password": "wrong"},
    )
    delete_response = client.delete(f"/api/posts/{post_id}?password=wrong")

    assert update_response.status_code == 403
    assert delete_response.status_code == 403
    assert client.get(f"/api/posts/{post_id}").status_code == 200


def test_missing_post_returns_404_for_detail_update_and_delete(client):
    assert client.get("/api/posts/999").status_code == 404
    assert client.put(
        "/api/posts/999",
        json={"title": "없음", "password": "1234"},
    ).status_code == 404
    assert client.delete("/api/posts/999?password=1234").status_code == 404


def test_partial_update_preserves_omitted_content(client):
    post = _create_post(client, title="수정 전", content="유지할 본문")

    response = client.put(
        f"/api/posts/{post['id']}",
        json={"title": "수정 후", "password": "1234"},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "수정 후"
    assert response.json()["content"] == "유지할 본문"


def test_list_posts_filters_by_category_and_never_returns_password(client):
    _create_post(client, title="관광 글", category="관광지")
    _create_post(client, title="음식 글", category="음식점")

    response = client.get("/api/posts?category=음식점")

    assert response.status_code == 200
    assert [post["title"] for post in response.json()] == ["음식 글"]
    assert all("password" not in post for post in response.json())


def test_list_posts_supports_pagination(client):
    _create_post(client, title="첫 번째")
    _create_post(client, title="두 번째")
    _create_post(client, title="세 번째")

    response = client.get("/api/posts?page=2&limit=1")

    assert response.status_code == 200
    assert [post["title"] for post in response.json()] == ["두 번째"]


def test_update_rejects_empty_title_or_content(client):
    post = _create_post(client, title="유효한 제목")

    empty_title = client.put(
        f"/api/posts/{post['id']}",
        json={"title": "", "password": "1234"},
    )
    empty_content = client.put(
        f"/api/posts/{post['id']}",
        json={"content": "", "password": "1234"},
    )

    assert empty_title.status_code == 422
    assert empty_content.status_code == 422


def test_openapi_contains_response_schemas(client):
    schemas = client.get("/openapi.json").json()["components"]["schemas"]

    assert "ContentTypeResponse" in schemas
    assert "PlaceListResponse" in schemas
    assert "PlaceDetailResponse" in schemas
    assert "PostResponse" in schemas
    assert "DeleteResponse" in schemas


def _create_post(
    client: TestClient,
    *,
    title: str,
    content: str = "본문",
    category: str = "관광지",
) -> dict:
    response = client.post(
        "/api/posts",
        json={
            "title": title,
            "content": content,
            "password": "1234",
            "category": category,
        },
    )
    assert response.status_code == 201
    return response.json()
