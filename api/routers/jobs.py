from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
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
    db_job = Job(**job.model_dump(exclude={'createdby'}), createdby=current_user.id)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return BaseResponse(
        success=True,
        message="Job created successfully",
        object=JobResponse.model_validate(db_job.__dict__).model_dump()
    )

@router.get("", response_model=PaginatedResponse)
def browse_jobs(
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    offset = (page - 1) * page_size
    jobs = db.query(Job).offset(offset).limit(page_size).all()
    total_size = db.query(Job).count()
    return PaginatedResponse(
        success=True,
        message="Jobs retrieved successfully",
        object=[JobResponse.model_validate(job.__dict__).model_dump() for job in jobs],
        pagenumber=page,
        pagesize=page_size,
        totalsize=total_size
    )
