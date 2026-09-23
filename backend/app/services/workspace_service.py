from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.organization import Organization, OrganizationMember
from app.models.user import User
from app.schemas.organization import OrganizationRole


class WorkspaceService:
    """Persistence and tenant-scope checks for workspace resources."""

    def create_personal_workspace(self, session: Session, user: User) -> Organization:
        workspace = Organization(name=f"{user.email.split('@')[0]}'s workspace", is_personal=True)
        session.add(workspace)
        session.flush()
        session.add(
            OrganizationMember(
                organization_id=workspace.id,
                user_id=user.id,
                role=OrganizationRole.OWNER.value,
            )
        )
        return workspace

    def create_workspace(self, session: Session, user: User, name: str) -> Organization:
        workspace = Organization(name=name.strip(), is_personal=False)
        session.add(workspace)
        session.flush()
        session.add(
            OrganizationMember(
                organization_id=workspace.id,
                user_id=user.id,
                role=OrganizationRole.OWNER.value,
            )
        )
        session.commit()
        session.refresh(workspace)
        return workspace

    def list_workspaces(self, session: Session, user: User) -> list[tuple[Organization, str]]:
        memberships = session.scalars(
            select(OrganizationMember)
            .join(Organization)
            .where(OrganizationMember.user_id == user.id)
            .options(joinedload(OrganizationMember.organization))
            .order_by(Organization.is_personal.desc(), Organization.name)
        ).all()
        return [(membership.organization, membership.role) for membership in memberships]

    def get_membership(self, session: Session, organization_id: str, user_id: str) -> OrganizationMember | None:
        return session.scalar(
            select(OrganizationMember)
            .where(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.user_id == user_id,
            )
            .options(joinedload(OrganizationMember.organization))
        )

    def add_member(
        self, session: Session, organization: Organization, email: str, role: OrganizationRole
    ) -> tuple[OrganizationMember, User]:
        user = session.scalar(select(User).where(User.email == email.lower()))
        if user is None:
            raise LookupError("No account exists for this email address.")
        existing = session.scalar(
            select(OrganizationMember).where(
                OrganizationMember.organization_id == organization.id,
                OrganizationMember.user_id == user.id,
            )
        )
        if existing is not None:
            raise ValueError("This user is already a workspace member.")
        membership = OrganizationMember(
            organization_id=organization.id,
            user_id=user.id,
            role=role.value,
        )
        session.add(membership)
        session.commit()
        session.refresh(membership)
        return membership, user

    def list_members(self, session: Session, organization_id: str) -> list[tuple[OrganizationMember, User]]:
        rows = session.execute(
            select(OrganizationMember, User)
            .join(User, User.id == OrganizationMember.user_id)
            .where(OrganizationMember.organization_id == organization_id)
            .order_by(User.email)
        ).all()
        return [(membership, user) for membership, user in rows]
