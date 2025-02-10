from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

class Member(BaseModel):
    id: int
    identifier: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    inactive_flag: bool = False

class Status(BaseModel):
    id: int
    name: str
    
class Project(BaseModel):
    id: int
    name: str
    status: Optional[Status] = None
    manager: Optional[Member] = None
    company_name: Optional[str] = Field(None, alias='company/name')
    estimated_hours: Optional[float] = Field(None, alias='estimatedHours')
    actual_hours: Optional[float] = Field(None, alias='actualHours')
    scheduled_start: Optional[datetime] = Field(None, alias='scheduledStart')
    scheduled_finish: Optional[datetime] = Field(None, alias='scheduledFinish')
    billing_method: Optional[str] = Field(None, alias='billingMethod')

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class TimeEntry(BaseModel):
    id: int
    time_start: datetime = Field(..., alias='timeStart')
    time_end: Optional[datetime] = Field(None, alias='timeEnd')
    hours_worked: float = Field(..., alias='hoursWorked')
    notes: Optional[str] = None
    member_identifier: Optional[str] = Field(None, alias='member/identifier')
    member_name: Optional[str] = Field(None, alias='member/name')
    charge_to_id: Optional[int] = Field(None, alias='chargeToId')
    charge_to_type: Optional[str] = Field(None, alias='chargeToType')

    class Config:
        populate_by_name = True

class Ticket(BaseModel):
    id: int
    summary: str
    status: Optional[Status] = None
    priority_name: Optional[str] = Field(None, alias='priority/name')
    project_id: Optional[int] = Field(None, alias='project/id')
    project_name: Optional[str] = Field(None, alias='project/name')
    assigned_to: Optional[str] = Field(None, alias='assignedTo/identifier')
    date_entered: datetime = Field(..., alias='dateEntered')
    estimated_hours: Optional[float] = Field(None, alias='estimatedHours')
    actual_hours: Optional[float] = Field(None, alias='actualHours')

    class Config:
        populate_by_name = True

class Note(BaseModel):
    id: int
    text: str
    detail_description_flag: Optional[bool] = Field(None, alias='detailDescriptionFlag')
    internal_analysis_flag: Optional[bool] = Field(None, alias='internalAnalysisFlag')
    resolution_flag: Optional[bool] = Field(None, alias='resolutionFlag')
    date_created: datetime = Field(..., alias='dateCreated')
    created_by: Optional[str] = Field(None, alias='createdBy')
    ticket_id: Optional[int] = None
    project_id: Optional[int] = None

    class Config:
        populate_by_name = True

# Response Models
class PaginatedResponse(BaseModel):
    page: int = 1
    page_size: int = 100
    total_count: int
    total_pages: int
    items: List[Dict]  # Generic for any item type

class ProjectSummary(BaseModel):
    project: Project
    total_hours: float
    billable_hours: float
    team_members: List[str]
    last_activity: Optional[datetime] 