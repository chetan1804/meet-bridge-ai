from __future__ import annotations

import base64
import binascii
from datetime import UTC, datetime, timedelta
import hashlib
import hmac
import json
import secrets
from typing import Any

from fastapi import HTTPException, status

from app.core.config import get_settings


PASSWORD_ITERATIONS = 600_000
JWT_HEADER = {"alg": "HS256", "typ": "JWT"}


def hash_password(password: str) -> str:
    """Create a salted PBKDF2-SHA256 password hash using a current work factor."""

    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, PASSWORD_ITERATIONS)
    return f"pbkdf2_sha256${PASSWORD_ITERATIONS}${_encode(salt)}${_encode(digest)}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify a password without exposing comparison timing information."""

    try:
        scheme, iteration_value, salt_value, expected_digest = stored_hash.split("$", maxsplit=3)
        if scheme != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), _decode(salt_value), int(iteration_value)
        )
        return hmac.compare_digest(_encode(digest), expected_digest)
    except (TypeError, ValueError):
        return False


def create_access_token(subject: str) -> str:
    settings = get_settings()
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": subject, "exp": int(expires_at.timestamp())}
    signing_input = f"{_json_segment(JWT_HEADER)}.{_json_segment(payload)}"
    signature = hmac.new(settings.jwt_secret_key.encode(), signing_input.encode(), hashlib.sha256).digest()
    return f"{signing_input}.{_encode(signature)}"


def decode_access_token(token: str) -> dict[str, Any]:
    """Validate an HS256 access token and return its payload."""

    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        header_value, payload_value, signature_value = token.split(".")
        header = json.loads(_decode(header_value))
        payload = json.loads(_decode(payload_value))
        expected_signature = hmac.new(
            get_settings().jwt_secret_key.encode(),
            f"{header_value}.{payload_value}".encode(),
            hashlib.sha256,
        ).digest()
        if header != JWT_HEADER or not hmac.compare_digest(_encode(expected_signature), signature_value):
            raise ValueError
        if not isinstance(payload.get("sub"), str) or int(payload["exp"]) <= int(datetime.now(UTC).timestamp()):
            raise ValueError
        return payload
    except (binascii.Error, KeyError, TypeError, ValueError, json.JSONDecodeError):
        raise credentials_error


def _json_segment(value: dict[str, Any]) -> str:
    return _encode(json.dumps(value, separators=(",", ":"), sort_keys=True).encode())


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode()


def _decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
