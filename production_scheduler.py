# -*- coding: utf-8 -*-

"""
Main module for the Production Scheduler application.
This file will contain the core business logic for scheduling production jobs.
"""

import uuid
from datetime import date, timedelta
class Job:
    """Represents a single production job."""
    def __init__(self, item: str, name: str, pieces_per_hour: int, total_pieces: int):
        if not all([item, name, pieces_per_hour > 0, total_pieces > 0]):
            raise ValueError("Invalid job data. Please check input values.")

        self.id = str(uuid.uuid4())
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
        # Default working hours: Mon-Fri 8 hours, Sat 4 hours, Sun 0 hours
        self.daily_working_hours = {
            0: 8, 1: 8, 2: 8, 3: 8, 4: 8, 5: 4, 6: 0
        }

    def set_schedule_period(self, start_date: date, end_date: date):
        """Sets the start and end dates for the production schedule."""
        if start_date > end_date:
            raise ValueError("Start date cannot be after end date.")
        self.start_date = start_date
        self.end_date = end_date
        print(f"Schedule period set from {start_date} to {end_date}")

    def set_daily_working_hours(self, hours_per_day: dict):
        """Sets the working hours for each day of the week (0=Monday, 6=Sunday)."""
        if not all(0 <= day <= 6 and isinstance(hours, (int, float)) and hours >= 0 for day, hours in hours_per_day.items()):
            raise ValueError("Invalid daily working hours format.")
        # Create a new dictionary to ensure we don't modify the default
        new_hours = self.daily_working_hours.copy()
        new_hours.update(hours_per_day)
        self.daily_working_hours = new_hours
        print("Daily working hours updated.")
        print(f"Current working hours: {self.daily_working_hours}")

    def add_job(self, job: Job):
        """Adds a new job to the list."""
        if job.id in self._job_map:
            raise ValueError(f"Job with ID {job.id} already exists.")
        self.jobs.append(job)
        self._job_map[job.id] = job
        print(f"Added Job: {job.item} - {job.name}")

    def remove_job(self, job_id: str):
        """Removes a job from the list by its ID."""
        if job_id not in self._job_map:
            raise ValueError(f"Job with ID {job_id} not found.")
        job_to_remove = self._job_map.pop(job_id)
        self.jobs.remove(job_to_remove)
        print(f"Removed Job: {job_to_remove.item} - {job_to_remove.name}")

    def update_job(self, job_id: str, **kwargs):
        """Updates a job's attributes."""
        if job_id not in self._job_map:
            raise ValueError(f"Job with ID {job_id} not found.")
        job_to_update = self._job_map[job_id]
        for key, value in kwargs.items():
            if hasattr(job_to_update, key):
                setattr(job_to_update, key, value)
            else:
                raise AttributeError(f"Job does not have attribute '{key}'")
        print(f"Updated Job: {job_to_update.item} - {job_to_update.name}")

    def get_job_by_id(self, job_id: str) -> Job:
        """Finds a job by its ID."""
        if job_id not in self._job_map:
            raise ValueError(f"Job with ID {job_id} not found.")
        return self._job_map[job_id]

    def list_jobs(self):
        """Lists all current jobs."""
        if not self.jobs:
            print("No jobs in the scheduler.")
            return
        print("\nCurrent Jobs List:")
        for job in self.jobs:
            print(f"- {job.item} ({job.name}), Requires: {job.get_required_hours():.2f} hrs")

    def schedule_jobs(self):
        """Automatically schedules the jobs based on priority and available hours."""
        if not self.start_date or not self.end_date:
            raise ValueError("Schedule period is not set. Please use set_schedule_period().")
        if not self.jobs:
            print("No jobs to schedule.")
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
            schedule[current_date] = []

            while available_hours > 0 and job_index < len(job_queue):
                current_job_item = job_queue[job_index]
                job = current_job_item["job"]
                hours_to_work = min(available_hours, current_job_item["remaining_hours"])

                schedule[current_date].append({
                    "item": job.item,
                    "name": job.name,
                    "hours_worked": hours_to_work
                })

                current_job_item["remaining_hours"] -= hours_to_work
                available_hours -= hours_to_work

                if current_job_item["remaining_hours"] <= 0:
                    job_index += 1  # Move to the next job

            current_date += timedelta(days=1)

        if job_index < len(job_queue):
            print("\nWarning: Not all jobs could be scheduled within the given period.")
            print(f"Jobs remaining: {len(self.jobs) - job_index}")

        return schedule

    def print_schedule(self, schedule: dict):
        """Prints the generated schedule in a readable format."""
        print("\n--- Production Schedule ---")
        if not schedule:
            print("The schedule is empty.")
            return

        sorted_dates = sorted(schedule.keys())
        for schedule_date in sorted_dates:
            tasks = schedule[schedule_date]
            day_str = schedule_date.strftime("%A, %Y-%m-%d")
            if tasks:
                print(f"\n📅 {day_str}:")
                for task in tasks:
                    print(f"  - Task: {task['item']} ({task['name']}), Duration: {task['hours_worked']:.2f} hours")
            else:
                print(f"\n📅 {day_str}: No tasks scheduled (Day off or no work planned).")


def main_cli() -> None:
    """Runs the command-line interface for the Production Scheduler."""
    scheduler = Scheduler()
    print("--- Welcome to the Production Scheduler CLI ---")

    # --- Setup with some default data for easier demonstration ---
    print("\nSetting up with default data for demonstration purposes...")
    today = date.today()
    scheduler.set_schedule_period(start_date=today, end_date=today + timedelta(days=30))
    scheduler.add_job(Job(item="PN-001", name="Product A", pieces_per_hour=100, total_pieces=1200)) # 12 hrs
    scheduler.add_job(Job(item="PN-002", name="Product B", pieces_per_hour=50, total_pieces=800))   # 16 hrs
    scheduler.add_job(Job(item="PN-003", name="Component C", pieces_per_hour=200, total_pieces=1600))# 8 hrs
    print("--------------------------------------")

    while True:
        print("\nMain Menu:")
        print("1. List all jobs")
        print("2. Add a new job")
        print("3. Remove a job")
        print("4. Generate and show schedule")
        print("5. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            scheduler.list_jobs()
        elif choice == '2':
            try:
                item = input("Enter Item Code: ")
                name = input("Enter Product Name: ")
                pph = int(input("Enter Pieces per Hour: "))
                total = int(input("Enter Total Pieces to Produce: "))
                scheduler.add_job(Job(item=item, name=name, pieces_per_hour=pph, total_pieces=total))
            except ValueError:
                print("Invalid input. Please enter numbers for hours and pieces.")
        elif choice == '3':
            job_id_to_remove = input("Enter the full ID of the job to remove: ")
            try:
                scheduler.remove_job(job_id_to_remove)
            except ValueError as e:
                print(f"Error: {e}")
        elif choice == '4':
            print("\n--- Generating Production Schedule ---")
            try:
                final_schedule = scheduler.schedule_jobs()
                scheduler.print_schedule(final_schedule)
            except ValueError as e:
                print(f"Error: {e}")
        elif choice == '5':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == '__main__':
    main_cli()
