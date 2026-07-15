from fastapi.testclient import TestClient

from app.main import app


def test_chat_without_api_key_returns_configuration_message(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with TestClient(app) as client:
        response = client.post(
            "/api/chat",
            json={"message": "대전 관광지를 추천해줘", "history": []},
        )

    assert response.status_code == 200
    assert "OPENAI_API_KEY가 설정되지 않았습니다" in response.json()["reply"]
