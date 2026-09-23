from enum import StrEnum

from pydantic import BaseModel, Field


class OrganizationRole(StrEnum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"


class OrganizationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)


class OrganizationResponse(BaseModel):
    id: str
    name: str
    is_personal: bool
    role: OrganizationRole


class OrganizationMemberCreate(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    role: OrganizationRole = OrganizationRole.MEMBER


class OrganizationMemberResponse(BaseModel):
    user_id: str
    email: str
    role: OrganizationRole
