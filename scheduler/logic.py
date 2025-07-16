# -*- coding: utf-8 -*-

"""
Core business logic for the Production Scheduler application.
Contains the Job and Scheduler classes.
"""

import uuid
from datetime import date, timedelta

class Job:
    """Represents a single production job."""
    def __init__(self, item: str, name: str, pieces_per_hour: int, total_pieces: int, job_id: str = None):
        if not all([item, name, pieces_per_hour > 0, total_pieces > 0]):
            raise ValueError("Invalid job data. Please check input values.")

        self.id = job_id or str(uuid.uuid4())
        self.item = item
        self.name = name
        self.pieces_per_hour = pieces_per_hour
        self.total_pieces = total_pieces

    def get_required_hours(self) -> float:
        """Calculates the total hours required to complete the job."""
        return self.total_pieces / self.pieces_per_hour

    def __repr__(self) -> str:
        return f"Job(id={self.id}, item='{self.item}', name='{self.name}')"


class Scheduler:
    """Manages a list of jobs and the production schedule."""
    def __init__(self):
        self.jobs = []
        self._job_map = {}
        self.start_date = None
        self.end_date = None
        self.daily_working_hours = {
            0: 8, 1: 8, 2: 8, 3: 8, 4: 8, 5: 4, 6: 0
        }

    def set_schedule_period(self, start_date: date, end_date: date):
        if start_date > end_date:
            raise ValueError("Start date cannot be after end date.")
        self.start_date = start_date
        self.end_date = end_date

    def set_daily_working_hours(self, hours_per_day: dict):
        if not all(0 <= day <= 6 and isinstance(hours, (int, float)) and hours >= 0 for day, hours in hours_per_day.items()):
            raise ValueError("Invalid daily working hours format.")
        new_hours = self.daily_working_hours.copy()
        new_hours.update(hours_per_day)
        self.daily_working_hours = new_hours

    def add_job(self, job: Job):
        if job.id in self._job_map:
            raise ValueError(f"Job with ID {job.id} already exists.")
        self.jobs.append(job)
        self._job_map[job.id] = job
        return job

    def remove_job(self, job_id: str):
        if job_id not in self._job_map:
            raise ValueError(f"Job with ID {job_id} not found.")
        job_to_remove = self._job_map.pop(job_id)
        self.jobs.remove(job_to_remove)
        return job_to_remove

    def update_job(self, job_id: str, **kwargs):
        if job_id not in self._job_map:
            raise ValueError(f"Job with ID {job_id} not found.")
        job_to_update = self._job_map[job_id]
        for key, value in kwargs.items():
            if hasattr(job_to_update, key):
                setattr(job_to_update, key, value)
        return job_to_update

    def get_job_by_id(self, job_id: str) -> Job:
        if job_id not in self._job_map:
            raise ValueError(f"Job with ID {job_id} not found.")
        return self._job_map[job_id]

    def list_jobs(self) -> list[Job]:
        return self.jobs

    def schedule_jobs(self):
        if not self.start_date or not self.end_date:
            raise ValueError("Schedule period is not set.")
        if not self.jobs:
            return {}

        schedule = {}
        current_date = self.start_date
        job_queue = [
            {"job": job, "remaining_hours": job.get_required_hours()} for job in self.jobs
        ]
        job_index = 0

        while current_date <= self.end_date and job_index < len(job_queue):
            day_of_week = current_date.weekday()
            available_hours = self.daily_working_hours.get(day_of_week, 0)
            schedule[current_date.isoformat()] = []

            while available_hours > 0 and job_index < len(job_queue):
                current_job_item = job_queue[job_index]
                job = current_job_item["job"]
                hours_to_work = min(available_hours, current_job_item["remaining_hours"])

                if hours_to_work > 0:
                    schedule[current_date.isoformat()].append({
                        "item": job.item,
                        "name": job.name,
                        "hours_worked": hours_to_work
                    })

                current_job_item["remaining_hours"] -= hours_to_work
                available_hours -= hours_to_work

                if current_job_item["remaining_hours"] <= 0.001: # Use tolerance for float comparison
                    job_index += 1

            current_date += timedelta(days=1)

        return schedule
