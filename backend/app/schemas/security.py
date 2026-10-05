from datetime import datetime, timezone

from pydantic import BaseModel, Field


class AuditEventRequest(BaseModel):
    action: str = Field(..., min_length=2)
    resource: str = Field(..., min_length=2)
    details: str = Field(default="")


class AuditEvent(BaseModel):
    action: str
    resource: str
    details: str = ""
    actor: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class RateLimitCheckRequest(BaseModel):
    action: str = Field(..., min_length=2)
    limit: int = Field(default=10, ge=1)
    window_seconds: int = Field(default=60, ge=1)


class RateLimitStatus(BaseModel):
    action: str
    limit: int
    current: int
    allowed: bool
    retry_after_seconds: int | None = None


class SecureUploadRequest(BaseModel):
    filename: str = Field(..., min_length=1)
    content: str = Field(default="")


class SecureUploadResponse(BaseModel):
    filename: str
    storage_key: str
    encrypted: bool = True
    secure: bool = True
    retention_days: int = 30
