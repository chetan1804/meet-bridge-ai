from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.routes.auth import get_current_user
from app.api.routes.organizations import get_tenant_membership
from app.db.session import get_db_session
from app.models.meeting import Meeting
from app.models.user import User
from app.schemas.meeting import MeetingCreate, MeetingResponse, MeetingUpdate

router=APIRouter(prefix="/organizations/{organization_id}/meetings", tags=["meetings"])
DB=Annotated[Session,Depends(get_db_session)]; Current=Annotated[User,Depends(get_current_user)]
@router.get("",response_model=list[MeetingResponse])
def list_meetings(organization_id:str, _:Annotated[object,Depends(get_tenant_membership)], session:DB):
 return list(session.scalars(select(Meeting).where(Meeting.organization_id==organization_id).order_by(Meeting.created_at.desc())))
@router.post("",response_model=MeetingResponse,status_code=status.HTTP_201_CREATED)
def create_meeting(organization_id:str,payload:MeetingCreate,_:Annotated[object,Depends(get_tenant_membership)],session:DB,current_user:Current):
 meeting=Meeting(organization_id=organization_id,created_by_id=current_user.id,title=payload.title.strip(),scheduled_at=payload.scheduled_at); session.add(meeting); session.commit(); session.refresh(meeting); return meeting
@router.get("/{meeting_id}",response_model=MeetingResponse)
def get_meeting(organization_id:str,meeting_id:str,_:Annotated[object,Depends(get_tenant_membership)],session:DB):
 meeting=session.scalar(select(Meeting).where(Meeting.id==meeting_id,Meeting.organization_id==organization_id))
 if not meeting: raise HTTPException(404,"Meeting not found.")
 return meeting
@router.patch("/{meeting_id}",response_model=MeetingResponse)
def update_meeting(organization_id:str,meeting_id:str,payload:MeetingUpdate,_:Annotated[object,Depends(get_tenant_membership)],session:DB):
 meeting=session.scalar(select(Meeting).where(Meeting.id==meeting_id,Meeting.organization_id==organization_id))
 if not meeting: raise HTTPException(404,"Meeting not found.")
 for key,value in payload.model_dump(exclude_unset=True).items(): setattr(meeting,key,value.strip() if key=="title" else value)
 session.commit(); session.refresh(meeting); return meeting
