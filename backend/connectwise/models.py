from pydantic import BaseModel, Field, ConfigDict, EmailStr, constr, conint, confloat, field_validator
from typing import Optional, List, Dict, Literal
from datetime import datetime
import re

class Member(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    id: int = Field(gt=0)
    identifier: constr(min_length=1, max_length=50)
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None
    inactive_flag: bool = False

    @field_validator('identifier')
    @classmethod
    def validate_identifier(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9._-]+$', v):
            raise ValueError('Identifier must contain only alphanumeric characters, dots, underscores, and hyphens')
        return v

class Status(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    id: int = Field(gt=0)
    name: constr(min_length=1, max_length=50)
    
class Project(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        ser_json_timedelta='iso8601'  # Modern way to handle datetime serialization
    )
    
    id: int = Field(gt=0)
    name: constr(min_length=1, max_length=100)
    status: Optional[Status] = None
    manager: Optional[Member] = None
    company_name: Optional[str] = Field(None, alias='company/name', max_length=100)
    estimated_hours: Optional[confloat(ge=0)] = Field(None, alias='estimatedHours')
    actual_hours: Optional[confloat(ge=0)] = Field(None, alias='actualHours')
    scheduled_start: Optional[datetime] = Field(None, alias='scheduledStart')
    scheduled_finish: Optional[datetime] = Field(None, alias='scheduledFinish')
    billing_method: Optional[Literal['FixedFee', 'TimeAndMaterials', 'NotToExceed']] = Field(None, alias='billingMethod')

    @field_validator('scheduled_finish')
    @classmethod
    def validate_dates(cls, v: Optional[datetime], info) -> Optional[datetime]:
        if v and info.data.get('scheduled_start'):
            if v < info.data['scheduled_start']:
                raise ValueError('Scheduled finish must be after scheduled start')
        return v

class TimeEntry(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    id: int = Field(gt=0)
    time_start: datetime = Field(..., alias='timeStart')
    time_end: Optional[datetime] = Field(None, alias='timeEnd')
    hours_worked: confloat(gt=0, lt=24) = Field(..., alias='hoursWorked')
    notes: Optional[str] = Field(None, max_length=2000)
    member_identifier: Optional[str] = Field(None, alias='member/identifier', max_length=50)
    member_name: Optional[str] = Field(None, alias='member/name', max_length=100)
    charge_to_id: Optional[int] = Field(None, alias='chargeToId', gt=0)
    charge_to_type: Optional[Literal['Project', 'Ticket', 'Activity']] = Field(None, alias='chargeToType')

    @field_validator('time_end')
    @classmethod
    def validate_time_end(cls, v: Optional[datetime], info) -> Optional[datetime]:
        if v and info.data.get('time_start'):
            if v < info.data['time_start']:
                raise ValueError('Time end must be after time start')
        return v

class Ticket(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    id: int = Field(gt=0)
    summary: constr(min_length=1, max_length=500)
    status: Optional[Status] = None
    priority_name: Optional[str] = Field(None, alias='priority/name', max_length=50)
    project_id: Optional[int] = Field(None, alias='project/id', gt=0)
    project_name: Optional[str] = Field(None, alias='project/name', max_length=100)
    assigned_to: Optional[str] = Field(None, alias='assignedTo/identifier', max_length=50)
    date_entered: datetime = Field(..., alias='dateEntered')
    estimated_hours: Optional[confloat(ge=0)] = Field(None, alias='estimatedHours')
    actual_hours: Optional[confloat(ge=0)] = Field(None, alias='actualHours')

class Note(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    id: int = Field(gt=0)
    text: constr(min_length=1, max_length=5000)
    detail_description_flag: Optional[bool] = Field(None, alias='detailDescriptionFlag')
    internal_analysis_flag: Optional[bool] = Field(None, alias='internalAnalysisFlag')
    resolution_flag: Optional[bool] = Field(None, alias='resolutionFlag')
    date_created: datetime = Field(..., alias='dateCreated')
    created_by: Optional[str] = Field(None, alias='createdBy', max_length=50)
    ticket_id: Optional[int] = Field(None, gt=0)
    project_id: Optional[int] = Field(None, gt=0)

# Response Models
class PaginatedResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    page: conint(gt=0) = 1
    page_size: conint(gt=0, le=1000) = 100
    total_count: conint(ge=0)
    total_pages: conint(ge=0)
    items: List[Dict] = Field(default_factory=list, max_length=1000)  # Using max_length instead of max_items

class ProjectSummary(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    project: Project
    total_hours: confloat(ge=0)
    billable_hours: confloat(ge=0)
    team_members: List[str] = Field(default_factory=list, max_length=100)  # Using max_length instead of max_items
    last_activity: Optional[datetime]

    @field_validator('billable_hours')
    @classmethod
    def validate_billable_hours(cls, v: float, info) -> float:
        if 'total_hours' in info.data and v > info.data['total_hours']:
            raise ValueError('Billable hours cannot exceed total hours')
        return v 