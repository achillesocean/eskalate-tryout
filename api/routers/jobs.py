from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from schemas.schemas import JobCreate, JobResponse, BaseResponse, PaginatedResponse
from models.models import Job, UserRole
from api.dependencies import get_db, get_current_user, check_role
from models.models import User

router = APIRouter()

@router.post("", response_model=BaseResponse)
def create_job(job: JobCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    check_role(current_user, UserRole.company)
    if job.createdby != current_user.id:
        return BaseResponse(
            success=False,
            message="Unauthorized",
            errors=["Cannot create job for another user"]
        )
    db_job = Job(**job.dict(), createdby=current_user.id)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return BaseResponse(success=True, message="Job created successfully", object=JobResponse.from_orm(db_job).dict())

@router.get("", response_model=PaginatedResponse)
def browse_jobs(
    page: int = 1,
    page_size: int = 10,
    title: Optional[str] = None,
    location: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    offset = (page - 1) * page_size
    query = db.query(Job)
    if title:
        query = query.filter(Job.title.ilike(f"%{title}%"))
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    jobs = query.offset(offset).limit(page_size).all()
    total_size = query.count()
    return PaginatedResponse(
        success=True,
        message="Jobs retrieved successfully",
        object=[JobResponse.from_orm(job).dict() for job in jobs],
        pagenumber=page,
        pagesize=page_size,
        totalsize=total_size
    )