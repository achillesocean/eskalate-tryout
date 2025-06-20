from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime
from schemas.schemas import ApplicationCreate, ApplicationResponse, BaseResponse, PaginatedResponse
from models.models import Application, User, Job, UserRole, ApplicationStatus
from api.dependencies import get_db, get_current_user, check_role
import cloudinary
import cloudinary.uploader
from core.config import settings

router = APIRouter()

# Cloudinary configuration
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)

@router.post("", response_model=BaseResponse)
async def apply_for_job(
    application: ApplicationCreate,
    resume: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_role(current_user, UserRole.applicant)
    if application.applicantid != current_user.id:
        return BaseResponse(
            success=False,
            message="Unauthorized",
            errors=["Cannot apply for another user"]
        )
    
    # Check for duplicate application
    existing_application = db.query(Application).filter(
        Application.applicantid == application.applicantid,
        Application.jobid == application.jobid
    ).first()
    if existing_application:
        return BaseResponse(
            success=False,
            message="Duplicate application",
            errors=["You have already applied to this job"]
        )
    
    # Validate cover letter length
    if application.coverletter and len(application.coverletter) > 200:
        return BaseResponse(
            success=False,
            message="Invalid cover letter",
            errors=["Cover letter must be under 200 characters"]
        )
    
    # Validate resume is PDF
    if resume.content_type != "application/pdf":
        return BaseResponse(
            success=False,
            message="Invalid file format",
            errors=["Resume must be a PDF file"]
        )
    
    # Upload resume to Cloudinary
    try:
        upload_result = cloudinary.uploader.upload(
            resume.file,
            resource_type="raw",
            folder="resumes",
            public_id=f"resume_{application.applicantid}_{application.jobid}"
        )
        resume_url = upload_result["secure_url"]
        # Validate Cloudinary URL
        if not resume_url.startswith("https://res.cloudinary.com/"):
            return BaseResponse(
                success=False,
                message="Invalid Cloudinary URL",
                errors=["Failed to generate a valid resume URL"]
            )
    except Exception as e:
        return BaseResponse(
            success=False,
            message="Failed to upload resume",
            errors=[str(e)]
        )
    
    # Create application
    db_application = Application(
        applicantid=application.applicantid,
        jobid=application.jobid,
        resumelink=resume_url,
        coverletter=application.coverletter,
        status=ApplicationStatus.applied,
        applied_at=datetime.utcnow()
    )
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return BaseResponse(
        success=True,
        message="Application submitted successfully",
        object=ApplicationResponse.from_orm(db_application).dict()
    )

@router.get("", response_model=PaginatedResponse)
def track_applications(
    page: int = 1,
    page_size: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_role(current_user, UserRole.applicant)
    offset = (page - 1) * page_size
    applications = db.query(Application).filter(Application.applicantid == current_user.id).offset(offset).limit(page_size).all()
    total_size = db.query(Application).filter(Application.applicantid == current_user.id).count()
    return PaginatedResponse(
        success=True,
        message="Applications retrieved successfully",
        object=[ApplicationResponse.from_orm(app).dict() for app in applications],
        pagenumber=page,
        pagesize=page_size,
        totalsize=total_size
    )

@router.get("/jobs/{job_id}", response_model=PaginatedResponse)
def view_job_applications(
    job_id: UUID,
    page: int = 1,
    page_size: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_role(current_user, UserRole.company)
    job = db.query(Job).filter(Job.id == job_id, Job.createdby == current_user.id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found or not owned by user")
    offset = (page - 1) * page_size
    applications = db.query(Application).filter(Application.jobid == job_id).offset(offset).limit(page_size).all()
    total_size = db.query(Application).filter(Application.jobid == job_id).count()
    return PaginatedResponse(
        success=True,
        message="Applications retrieved successfully",
        object=[ApplicationResponse.from_orm(app).dict() for app in applications],
        pagenumber=page,
        pagesize=page_size,
        totalsize=total_size
    )