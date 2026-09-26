import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.db.base import Base
from app.main import app
from tests.conftest import engine


client = TestClient(app)


def setup_function() -> None:
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def _create_meeting() -> tuple[str, str, str]:
    credentials = {"email": "socket@example.com", "password": "a-long-secret-password"}
    token = client.post("/api/auth/register", json=credentials).json()["access_token"]
    workspace = client.get("/api/organizations", headers={"Authorization": f"Bearer {token}"}).json()[0]
    meeting = client.post(
        f"/api/organizations/{workspace['id']}/meetings",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Realtime meeting"},
    ).json()
    return token, workspace["id"], meeting["id"]


def test_authenticated_meeting_socket_supports_handshake_and_heartbeat() -> None:
    token, organization_id, meeting_id = _create_meeting()

    with client.websocket_connect(
        f"/api/ws/organizations/{organization_id}/meetings/{meeting_id}?token={token}"
    ) as websocket:
        assert websocket.receive_json() == {"type": "connected", "meeting_id": meeting_id}
        websocket.send_json({"type": "ping"})
        assert websocket.receive_json() == {"type": "pong"}


def test_meeting_socket_accepts_and_accounts_for_audio_chunks() -> None:
    token, organization_id, meeting_id = _create_meeting()

    with client.websocket_connect(
        f"/api/ws/organizations/{organization_id}/meetings/{meeting_id}?token={token}"
    ) as websocket:
        websocket.receive_json()
        websocket.send_json({"type": "audio_chunk", "mime_type": "audio/webm", "data": "YXVkaW8="})
        assert websocket.receive_json() == {
            "type": "audio_ack",
            "chunks_received": 1,
            "bytes_received": 5,
        }
        transcript = websocket.receive_json()
        assert transcript["type"] == "transcript"
        assert transcript["provider"] == "mock"
        assert transcript["is_final"] is False
        meeting_state = client.get("/api/meeting/state").json()
        assert transcript["text"] in meeting_state["transcript"]


def test_meeting_socket_rejects_invalid_audio_chunks() -> None:
    token, organization_id, meeting_id = _create_meeting()

    with client.websocket_connect(
        f"/api/ws/organizations/{organization_id}/meetings/{meeting_id}?token={token}"
    ) as websocket:
        websocket.receive_json()
        websocket.send_json({"type": "audio_chunk", "mime_type": "text/plain", "data": "not-base64"})
        response = websocket.receive_json()
        assert response["type"] == "error"
        assert "audio MIME type" in response["detail"]


def test_meeting_socket_rejects_missing_authentication() -> None:
    _, organization_id, meeting_id = _create_meeting()

    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect(f"/api/ws/organizations/{organization_id}/meetings/{meeting_id}"):
            pass


def test_meeting_socket_rejects_cross_tenant_access() -> None:
    _, organization_id, meeting_id = _create_meeting()
    other_credentials = {"email": "other-socket@example.com", "password": "a-long-secret-password"}
    other_token = client.post("/api/auth/register", json=other_credentials).json()["access_token"]

    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect(
            f"/api/ws/organizations/{organization_id}/meetings/{meeting_id}?token={other_token}"
        ):
            pass