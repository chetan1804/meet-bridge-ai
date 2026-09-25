import json
from typing import Annotated

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.routes.auth import service as auth_service
from app.core.security import decode_access_token
from app.db.session import get_db_session
from app.models.meeting import Meeting
from app.models.organization import OrganizationMember
from app.services.meeting_socket_manager import manager


router = APIRouter(tags=["meeting realtime"])
DatabaseSession = Annotated[Session, Depends(get_db_session)]


def _token_from_websocket(websocket: WebSocket) -> str | None:
    token = websocket.query_params.get("token")
    if token:
        return token
    authorization = websocket.headers.get("authorization", "")
    scheme, _, header_token = authorization.partition(" ")
    return header_token if scheme.lower() == "bearer" and header_token else None


def _authenticated_user_id(websocket: WebSocket, session: Session) -> str | None:
    token = _token_from_websocket(websocket)
    if token is None:
        return None
    try:
        payload = decode_access_token(token)
    except Exception:
        return None
    user = auth_service.get_user(session, payload["sub"])
    return user.id if user is not None and user.is_active else None


@router.websocket("/ws/organizations/{organization_id}/meetings/{meeting_id}")
async def meeting_socket(
    websocket: WebSocket,
    organization_id: str,
    meeting_id: str,
    session: DatabaseSession,
) -> None:
    user_id = _authenticated_user_id(websocket, session)
    if user_id is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    has_membership = session.scalar(
        select(OrganizationMember.id).where(
            OrganizationMember.organization_id == organization_id,
            OrganizationMember.user_id == user_id,
        )
    )
    meeting_exists = session.scalar(
        select(Meeting.id).where(
            Meeting.id == meeting_id,
            Meeting.organization_id == organization_id,
        )
    )
    if has_membership is None or meeting_exists is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(meeting_id, websocket)
    try:
        await websocket.send_json({"type": "connected", "meeting_id": meeting_id})
        while True:
            message = await websocket.receive_text()
            try:
                payload = json.loads(message)
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "detail": "Message must be valid JSON."})
                continue

            if payload.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            else:
                await websocket.send_json({"type": "ack", "message_type": payload.get("type", "unknown")})
    except WebSocketDisconnect:
        manager.disconnect(meeting_id, websocket)