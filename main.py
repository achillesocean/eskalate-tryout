from fastapi import FastAPI
from api.routers import auth, jobs, applications
from db.database import engine
from models.models import Base

app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
app.include_router(applications.router, prefix="/applications", tags=["applications"])