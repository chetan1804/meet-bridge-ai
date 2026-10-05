from __future__ import annotations

import hashlib
import re
import time
from collections import defaultdict, deque

from app.schemas.security import AuditEvent, RateLimitStatus, SecureUploadResponse


class SecurityService:
    def __init__(self) -> None:
        self._audit_log: list[dict[str, str]] = []
        self._rate_limits: dict[str, deque[float]] = defaultdict(deque)

    def record_audit(self, actor: str, action: str, resource: str, details: str = "") -> AuditEvent:
        entry = {
            "action": action,
            "resource": resource,
            "details": details,
            "actor": actor,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        self._audit_log.insert(0, entry)
        return AuditEvent(**entry)

    def list_audit(self, actor: str | None = None) -> list[AuditEvent]:
        events = self._audit_log
        if actor is not None:
            events = [entry for entry in events if entry["actor"] == actor]
        return [AuditEvent(**entry) for entry in events]

    def check_rate_limit(self, actor: str, action: str, limit: int = 10, window_seconds: int = 60) -> RateLimitStatus:
        key = f"{actor}:{action}"
        timestamps = self._rate_limits[key]
        now = time.time()

        while timestamps and now - timestamps[0] > window_seconds:
            timestamps.popleft()

        allowed = len(timestamps) < limit
        if allowed:
            timestamps.append(now)

        retry_after_seconds = None
        if not allowed and timestamps:
            oldest = timestamps[0]
            retry_after_seconds = max(0, int(window_seconds - (now - oldest)))

        return RateLimitStatus(
            action=action,
            limit=limit,
            current=len(timestamps),
            allowed=allowed,
            retry_after_seconds=retry_after_seconds,
        )

    def secure_upload(self, actor: str, filename: str, content: str) -> SecureUploadResponse:
        cleaned_name = re.sub(r"[^A-Za-z0-9._-]+", "-", filename).strip(".-") or "secure-upload"
        digest = hashlib.sha256(f"{actor}:{cleaned_name}:{content}".encode("utf-8")).hexdigest()[:32]
        return SecureUploadResponse(
            filename=cleaned_name,
            storage_key=f"secure/{digest}",
            encrypted=True,
            secure=True,
            retention_days=30,
        )


service = SecurityService()
