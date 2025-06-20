from sqlalchemy import Column, String, Enum, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import uuid
import enum
from datetime import datetime
from db import Base

class UserRole(enum.Enum):
    applicant = "applicant"
    company = "company"

class ApplicationStatus(enum.Enum):
    applied = "applied"
    reviewed = "reviewed"
    interviewed = "interviewed"
    rejected = "rejected"
    hired = "hired"

class User(Base):
    __tablename__ = "user"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)

    jobs = relationship("Job", back_populates="created_by")
    applications = relationship("Application", back_populates="applicant")

class Job(Base):
    __tablename__ = "job"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    location = Column(String, nullable=False)
    createdby = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    created_by = relationship("User", back_populates="jobs")
    applications = relationship("Application", back_populates="job")

class Application(Base):
    __tablename__ = "application"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    applicantid = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    jobid = Column(UUID(as_uuid=True), ForeignKey("job.id"), nullable=False)
    resumelink = Column(String, nullable=False)
    coverletter = Column(String, nullable=True)
    status = Column(Enum(ApplicationStatus), nullable=False, default=ApplicationStatus.applied)
    applied_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    applicant = relationship("User", back_populates="applications")
    job = relationship("Job", back_populates="applications")