# -*- coding: utf-8 -*-

"""
Main FastAPI application file.
This file defines the API endpoints for the Production Scheduler.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
import uuid
from datetime import date

# Import business logic
from scheduler.logic import Job, Scheduler

# --- Pydantic Models for API data validation ---

class JobBase(BaseModel):
    item: str = Field(..., example="PN-001")
    name: str = Field(..., example="Product A")
    pieces_per_hour: int = Field(..., gt=0, example=100)
    total_pieces: int = Field(..., gt=0, example=1000)

class JobCreate(JobBase):
    pass

class JobOut(JobBase):
    id: str = Field(..., example=str(uuid.uuid4()))
    required_hours: float = Field(..., example=10.0)

    class Config:
        orm_mode = True

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# --- FastAPI Application ---

app = FastAPI(
    title="Production Scheduler API",
    description="An API to manage and schedule production jobs.",
    version="1.0.0"
)

# --- Mount Static Files ---
app.mount("/static", StaticFiles(directory="static"), name="static")


# In-memory 'database'
scheduler_instance = Scheduler()

# --- API Endpoints ---

@app.get("/", response_class=FileResponse, tags=["General"])
def read_root():
    """Serve the main HTML file."""
    return "static/index.html"

@app.post("/jobs", response_model=JobOut, status_code=201, tags=["Jobs"])
def create_job(job_in: JobCreate):
    """
    Create a new production job.
    """
    job = Job(**job_in.dict())
    try:
        created_job = scheduler_instance.add_job(job)
        # Manually construct the response to include required_hours
        response = JobOut(
            id=created_job.id,
            item=created_job.item,
            name=created_job.name,
            pieces_per_hour=created_job.pieces_per_hour,
            total_pieces=created_job.total_pieces,
            required_hours=created_job.get_required_hours()
        )
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/jobs", response_model=List[JobOut], tags=["Jobs"])
def list_jobs():
    """
    Retrieve a list of all current production jobs.
    """
    jobs = scheduler_instance.list_jobs()
    # Convert logic Job objects to JobOut models
    response = [
        JobOut(
            id=job.id,
            item=job.item,
            name=job.name,
            pieces_per_hour=job.pieces_per_hour,
            total_pieces=job.total_pieces,
            required_hours=job.get_required_hours()
        ) for job in jobs
    ]
    return response

class ScheduleRequest(BaseModel):
    start_date: date = Field(..., example=date.today().isoformat())
    end_date: date = Field(..., example=(date.today() + timedelta(days=14)).isoformat())

@app.post("/schedule/calculate", tags=["Schedule"])
def calculate_schedule(request: ScheduleRequest):
    """
    Calculate the production schedule based on the current jobs.
    """
    if not scheduler_instance.list_jobs():
        raise HTTPException(status_code=400, detail="No jobs to schedule.")

    try:
        scheduler_instance.set_schedule_period(request.start_date, request.end_date)
        schedule_result = scheduler_instance.schedule_jobs()
        return {"schedule": schedule_result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
