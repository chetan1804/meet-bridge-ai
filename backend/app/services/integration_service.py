from __future__ import annotations

from app.schemas.integration import IntegrationDefinition


class IntegrationService:
    def __init__(self) -> None:
        self._registry: dict[str, dict[str, str]] = {
            "slack": {
                "name": "Slack",
                "description": "Post meeting summaries and action items to your workspace channels.",
                "credential_label": "Bot token",
            },
            "google_calendar": {
                "name": "Google Calendar",
                "description": "Create follow-up events and meeting reminders automatically.",
                "credential_label": "Service account key",
            },
        }
        self._credentials: dict[str, str] = {}

    def list_integrations(self) -> list[IntegrationDefinition]:
        items: list[IntegrationDefinition] = []
        for key, metadata in self._registry.items():
            secret = self._credentials.get(key)
            items.append(
                IntegrationDefinition(
                    key=key,
                    name=metadata["name"],
                    description=metadata["description"],
                    credential_label=metadata["credential_label"],
                    connected=secret is not None,
                    credential_preview=self._mask_secret(secret) if secret else None,
                )
            )
        return items

    def connect(self, key: str, token: str) -> IntegrationDefinition:
        normalized = key.strip().lower()
        if normalized not in self._registry:
            raise KeyError(f"Integration '{key}' is not supported.")
        credential = token.strip()
        if not credential:
            raise ValueError("A token is required to connect this integration.")
        self._credentials[normalized] = credential
        metadata = self._registry[normalized]
        return IntegrationDefinition(
            key=normalized,
            name=metadata["name"],
            description=metadata["description"],
            credential_label=metadata["credential_label"],
            connected=True,
            credential_preview=self._mask_secret(credential),
        )

    def disconnect(self, key: str) -> None:
        normalized = key.strip().lower()
        self._credentials.pop(normalized, None)

    @staticmethod
    def _mask_secret(secret: str) -> str:
        if len(secret) <= 4:
            return "*" * len(secret)
        kept = secret[-4:]
        hidden = "*" * (len(secret) - 4)
        return f"{hidden}{kept}"


service = IntegrationService()
