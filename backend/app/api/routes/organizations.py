from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.routes.auth import get_current_user
from app.db.session import get_db_session
from app.models.organization import Organization, OrganizationMember
from app.models.user import User
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationMemberCreate,
    OrganizationMemberResponse,
    OrganizationResponse,
    OrganizationRole,
)
from app.services.workspace_service import WorkspaceService


router = APIRouter(prefix="/organizations", tags=["organizations"])
service = WorkspaceService()
DatabaseSession = Annotated[Session, Depends(get_db_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


def get_tenant_membership(
    organization_id: str, session: DatabaseSession, current_user: CurrentUser
) -> OrganizationMember:
    """Return only a membership owned by the authenticated user; never reveal other tenants."""

    membership = service.get_membership(session, organization_id, current_user.id)
    if membership is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found.")
    return membership


def to_workspace_response(organization: Organization, role: str) -> OrganizationResponse:
    return OrganizationResponse(
        id=organization.id,
        name=organization.name,
        is_personal=organization.is_personal,
        role=OrganizationRole(role),
    )


@router.post("", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
def create_organization(payload: OrganizationCreate, session: DatabaseSession, current_user: CurrentUser) -> OrganizationResponse:
    organization = service.create_workspace(session, current_user, payload.name)
    return to_workspace_response(organization, OrganizationRole.OWNER.value)


@router.get("", response_model=list[OrganizationResponse])
def list_organizations(session: DatabaseSession, current_user: CurrentUser) -> list[OrganizationResponse]:
    return [to_workspace_response(organization, role) for organization, role in service.list_workspaces(session, current_user)]


@router.get("/{organization_id}", response_model=OrganizationResponse)
def get_organization(membership: Annotated[OrganizationMember, Depends(get_tenant_membership)]) -> OrganizationResponse:
    return to_workspace_response(membership.organization, membership.role)


@router.post("/{organization_id}/members", response_model=OrganizationMemberResponse, status_code=status.HTTP_201_CREATED)
def add_organization_member(
    payload: OrganizationMemberCreate,
    membership: Annotated[OrganizationMember, Depends(get_tenant_membership)],
    session: DatabaseSession,
) -> OrganizationMemberResponse:
    if membership.role not in {OrganizationRole.OWNER.value, OrganizationRole.ADMIN.value}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Workspace admin access is required.")
    try:
        new_membership, user = service.add_member(session, membership.organization, payload.email, payload.role)
    except LookupError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error))
    return OrganizationMemberResponse(user_id=user.id, email=user.email, role=OrganizationRole(new_membership.role))


@router.get("/{organization_id}/members", response_model=list[OrganizationMemberResponse])
def list_organization_members(
    membership: Annotated[OrganizationMember, Depends(get_tenant_membership)], session: DatabaseSession
) -> list[OrganizationMemberResponse]:
    return [
        OrganizationMemberResponse(user_id=user.id, email=user.email, role=OrganizationRole(member.role))
        for member, user in service.list_members(session, membership.organization_id)
    ]
