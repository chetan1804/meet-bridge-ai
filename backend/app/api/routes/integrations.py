from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.routes.auth import get_current_user
from app.models.user import User
from app.schemas.integration import IntegrationConnectRequest, IntegrationDefinition
from app.services.integration_service import service


router = APIRouter(prefix="/integrations", tags=["integrations"])
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get("", response_model=list[IntegrationDefinition])
def list_integrations(current_user: CurrentUser) -> list[IntegrationDefinition]:
    return service.list_integrations()


@router.post("/{integration_key}/connect", response_model=IntegrationDefinition)
def connect_integration(
    integration_key: str,
    payload: IntegrationConnectRequest,
    current_user: CurrentUser,
) -> IntegrationDefinition:
    try:
        return service.connect(integration_key, payload.token)
    except KeyError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error


@router.delete("/{integration_key}", status_code=status.HTTP_204_NO_CONTENT)
def disconnect_integration(integration_key: str, current_user: CurrentUser) -> None:
    service.disconnect(integration_key)
