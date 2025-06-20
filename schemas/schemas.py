from pydantic import BaseModel, EmailStr, HttpUrl
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    applicant = "applicant"
    company = "company"

class ApplicationStatus(str, Enum):
    applied = "applied"
    reviewed = "reviewed"
    interviewed = "interviewed"
    rejected = "rejected"
    hired = "hired"

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: UserRole

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: UUID

    class Config:
        from_attributes = True

class JobBase(BaseModel):
    title: str
    description: str
    location: str

class JobCreate(JobBase):
    createdby: UUID

class JobResponse(JobBase):
    id: UUID
    createdby: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class ApplicationBase(BaseModel):
    resumelink: HttpUrl
    coverletter: Optional[str] = None
    status: ApplicationStatus = ApplicationStatus.applied

class ApplicationCreate(BaseModel):
    applicantid: UUID
    jobid: UUID
    coverletter: Optional[str] = None

class ApplicationResponse(ApplicationBase):
    id: UUID
    applicantid: UUID
    jobid: UUID
    applied_at: datetime

    class Config:
        from_attributes = True

class BaseResponse(BaseModel):
    success: bool
    message: str
    object: Optional[dict] = None
    errors: Optional[List[str]] = None

    class Config:
        from_attributes = True

class PaginatedResponse(BaseModel):
    success: bool
    message: str
    object: List[dict]
    pagenumber: int
    pagesize: int
    totalsize: int
    errors: Optional[List[str]] = None