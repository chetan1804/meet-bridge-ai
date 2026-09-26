import json
from typing import Annotated

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.routes.auth import service as auth_service
from app.core.config import get_settings
from app.core.security import decode_access_token
from app.db.session import get_db_session
from app.models.meeting import Meeting
from app.models.organization import OrganizationMember
from app.schemas.audio import AudioChunkMessage
from app.services.audio_ingestion import audio_ingestion
from app.services.meeting_state_service import service as meeting_state_service
from app.services.meeting_socket_manager import manager
from app.services.speech_provider import get_speech_provider


router = APIRouter(tags=["meeting realtime"])
DatabaseSession = Annotated[Session, Depends(get_db_session)]
speech_provider = get_speech_provider(get_settings().speech_to_text_provider)


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
            elif payload.get("type") == "audio_chunk":
                try:
                    audio_message = AudioChunkMessage.model_validate(payload)
                    audio_session = audio_ingestion.accept(meeting_id, user_id, audio_message)
                except (ValidationError, ValueError) as error:
                    detail = error.errors()[0]["msg"] if isinstance(error, ValidationError) else str(error)
                    await websocket.send_json({"type": "error", "detail": detail})
                    continue
                await websocket.send_json(
                    {
                        "type": "audio_ack",
                        "chunks_received": audio_session.chunks_received,
                        "bytes_received": audio_session.bytes_received,
                    }
                )
                transcript = speech_provider.transcribe_chunk(audio_message)
                if transcript is not None:
                    meeting_state_service.add_transcript_line(transcript.text)
                    await websocket.send_json({"type": "transcript", **transcript.model_dump()})
            else:
                await websocket.send_json({"type": "ack", "message_type": payload.get("type", "unknown")})
    except WebSocketDisconnect:
        manager.disconnect(meeting_id, websocket)
        audio_ingestion.clear(meeting_id, user_id)