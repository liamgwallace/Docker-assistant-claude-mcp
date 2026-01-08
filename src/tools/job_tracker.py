"""
Job tracking system for asynchronous Docker management tasks
Uses file-based storage for simplicity
"""
import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, List
from enum import Enum

from src.config.environment import settings


class JobStatus(str, Enum):
    """Job execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Job:
    """Represents a background job"""

    def __init__(
        self,
        job_id: str,
        request: str,
        status: JobStatus = JobStatus.PENDING,
        output: Optional[str] = None,
        error: Optional[str] = None,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None
    ):
        self.job_id = job_id
        self.request = request
        self.status = status
        self.output = output
        self.error = error
        self.started_at = started_at or datetime.now()
        self.completed_at = completed_at

    def to_dict(self) -> Dict:
        """Convert job to dictionary for JSON serialization"""
        return {
            "job_id": self.job_id,
            "request": self.request,
            "status": self.status.value,
            "output": self.output,
            "error": self.error,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Job":
        """Create job from dictionary"""
        return cls(
            job_id=data["job_id"],
            request=data["request"],
            status=JobStatus(data["status"]),
            output=data.get("output"),
            error=data.get("error"),
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None
        )


class JobTracker:
    """Manages job lifecycle and persistence"""

    def __init__(self, jobs_dir: Optional[Path] = None):
        self.jobs_dir = jobs_dir or settings.jobs_dir
        self.jobs_dir.mkdir(parents=True, exist_ok=True)

    def _get_job_file(self, job_id: str) -> Path:
        """Get path to job file"""
        return self.jobs_dir / f"{job_id}.json"

    def create_job(self, request: str) -> Job:
        """
        Create a new job

        Args:
            request: User's request description

        Returns:
            Created job
        """
        job_id = str(uuid.uuid4())
        job = Job(job_id=job_id, request=request, status=JobStatus.PENDING)
        self._save_job(job)
        return job

    def get_job(self, job_id: str) -> Optional[Job]:
        """
        Get job by ID

        Args:
            job_id: Job ID

        Returns:
            Job or None if not found
        """
        job_file = self._get_job_file(job_id)

        if not job_file.exists():
            return None

        try:
            with open(job_file, 'r') as f:
                data = json.load(f)
            return Job.from_dict(data)
        except Exception as e:
            print(f"Error loading job {job_id}: {e}")
            return None

    def update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        output: Optional[str] = None,
        error: Optional[str] = None
    ) -> bool:
        """
        Update job status

        Args:
            job_id: Job ID
            status: New status
            output: Job output (for completed jobs)
            error: Error message (for failed jobs)

        Returns:
            True if updated, False if job not found
        """
        job = self.get_job(job_id)

        if not job:
            return False

        job.status = status

        if status == JobStatus.RUNNING and not job.started_at:
            job.started_at = datetime.now()

        if status in (JobStatus.COMPLETED, JobStatus.FAILED):
            job.completed_at = datetime.now()

        if output:
            job.output = output

        if error:
            job.error = error

        self._save_job(job)
        return True

    def _save_job(self, job: Job) -> None:
        """Save job to file"""
        job_file = self._get_job_file(job.job_id)

        try:
            with open(job_file, 'w') as f:
                json.dump(job.to_dict(), f, indent=2)
        except Exception as e:
            print(f"Error saving job {job.job_id}: {e}")

    def list_jobs(self, status: Optional[JobStatus] = None) -> List[Job]:
        """
        List all jobs, optionally filtered by status

        Args:
            status: Optional status filter

        Returns:
            List of jobs
        """
        jobs = []

        for job_file in self.jobs_dir.glob("*.json"):
            try:
                with open(job_file, 'r') as f:
                    data = json.load(f)
                job = Job.from_dict(data)

                if status is None or job.status == status:
                    jobs.append(job)
            except Exception as e:
                print(f"Error loading job from {job_file}: {e}")

        # Sort by started_at descending (newest first)
        jobs.sort(key=lambda j: j.started_at, reverse=True)
        return jobs

    def cleanup_old_jobs(self, max_age_hours: Optional[int] = None) -> int:
        """
        Remove jobs older than max_age_hours

        Args:
            max_age_hours: Maximum age in hours (default from settings)

        Returns:
            Number of jobs deleted
        """
        max_age = max_age_hours or settings.max_job_age_hours
        cutoff_time = datetime.now() - timedelta(hours=max_age)
        deleted_count = 0

        for job_file in self.jobs_dir.glob("*.json"):
            try:
                with open(job_file, 'r') as f:
                    data = json.load(f)
                job = Job.from_dict(data)

                # Delete if completed/failed and older than cutoff
                if job.status in (JobStatus.COMPLETED, JobStatus.FAILED):
                    if job.completed_at and job.completed_at < cutoff_time:
                        job_file.unlink()
                        deleted_count += 1
            except Exception as e:
                print(f"Error processing job file {job_file}: {e}")

        return deleted_count

    def delete_job(self, job_id: str) -> bool:
        """
        Delete a specific job

        Args:
            job_id: Job ID to delete

        Returns:
            True if deleted, False if not found
        """
        job_file = self._get_job_file(job_id)

        if job_file.exists():
            try:
                job_file.unlink()
                return True
            except Exception as e:
                print(f"Error deleting job {job_id}: {e}")
                return False

        return False
