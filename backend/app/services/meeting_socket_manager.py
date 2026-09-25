from collections import defaultdict

from fastapi import WebSocket


class MeetingSocketManager:
    """Track active sockets by meeting for the initial real-time transport."""

    def __init__(self) -> None:
        self._connections: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(self, meeting_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections[meeting_id].add(websocket)

    def disconnect(self, meeting_id: str, websocket: WebSocket) -> None:
        connections = self._connections.get(meeting_id)
        if connections is None:
            return
        connections.discard(websocket)
        if not connections:
            self._connections.pop(meeting_id, None)


manager = MeetingSocketManager()