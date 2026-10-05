from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.routes.auth import get_current_user
from app.models.user import User
from app.schemas.security import (
    AuditEvent,
    AuditEventRequest,
    RateLimitCheckRequest,
    RateLimitStatus,
    SecureUploadRequest,
    SecureUploadResponse,
)
from app.services.security_service import service


router = APIRouter(prefix="/security", tags=["security"])
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post("/audit", response_model=AuditEvent)
def record_audit(payload: AuditEventRequest, current_user: CurrentUser) -> AuditEvent:
    return service.record_audit(current_user.email, payload.action, payload.resource, payload.details)


@router.get("/audit", response_model=list[AuditEvent])
def list_audit(current_user: CurrentUser) -> list[AuditEvent]:
    return service.list_audit(current_user.email)


@router.post("/rate-limit/check", response_model=RateLimitStatus)
def check_rate_limit(payload: RateLimitCheckRequest, current_user: CurrentUser) -> RateLimitStatus:
    return service.check_rate_limit(current_user.email, payload.action, payload.limit, payload.window_seconds)


@router.post("/uploads/secure", response_model=SecureUploadResponse)
def create_secure_upload(payload: SecureUploadRequest, current_user: CurrentUser) -> SecureUploadResponse:
    return service.secure_upload(current_user.email, payload.filename, payload.content)
