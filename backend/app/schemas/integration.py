from pydantic import BaseModel, Field


class IntegrationConnectRequest(BaseModel):
    token: str = Field(..., min_length=4, description="Credential used to connect the integration.")


class IntegrationDefinition(BaseModel):
    key: str
    name: str
    description: str
    credential_label: str
    connected: bool = False
    credential_preview: str | None = None
