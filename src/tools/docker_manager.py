"""
Docker management tool handlers for MCP server
Provides three tools: docker_execute, docker_execute_async, docker_job_status
"""
import asyncio
from typing import Dict, Any

from src.tools.claude_code_executor import ClaudeCodeExecutor
from src.tools.job_tracker import JobTracker, JobStatus


class DockerManager:
    """Manages Docker operations through Claude Code CLI"""

    def __init__(self):
        self.executor = ClaudeCodeExecutor()
        self.job_tracker = JobTracker()

    async def docker_execute(self, request: str) -> Dict[str, Any]:
        """
        Execute Docker/Portainer management task synchronously
        Waits for task completion and returns full output

        Args:
            request: User's natural language request for Docker management

        Returns:
            Tool response with markdown content
        """
        # Execute synchronously via Claude Code
        result = await self.executor.execute_sync(request)

        return {
            "content": [
                {
                    "type": "text",
                    "text": result
                }
            ]
        }

    async def docker_execute_async(self, request: str) -> Dict[str, Any]:
        """
        Execute Docker management task asynchronously in background
        Returns immediately with job ID

        Args:
            request: User's natural language request for Docker management

        Returns:
            Tool response with job ID
        """
        # Create job
        job = self.job_tracker.create_job(request)

        # Start background task
        asyncio.create_task(self._execute_background_job(job.job_id, request))

        # Return immediately with job ID
        response_text = f"""## Task Started in Background

**Job ID:** `{job.job_id}`

Your Docker management task has been queued for execution.

### Request
{request}

### Check Status
Use the `docker_job_status` tool with this job ID to check progress and get results:

```json
{{
  "job_id": "{job.job_id}"
}}
```

### Status Options
- **running**: Task is currently executing
- **completed**: Task finished successfully
- **failed**: Task encountered an error
"""

        return {
            "content": [
                {
                    "type": "text",
                    "text": response_text
                }
            ]
        }

    async def docker_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Check status of an asynchronous Docker management job

        Args:
            job_id: Job ID returned from docker_execute_async

        Returns:
            Tool response with job status and output
        """
        job = self.job_tracker.get_job(job_id)

        if not job:
            response_text = f"""## Job Not Found

**Job ID:** `{job_id}`

This job ID was not found in the system.

### Possible Causes
- Job ID is incorrect or expired
- Job was deleted due to age (jobs older than 24 hours are auto-deleted)
- Job never existed

### Next Steps
- Verify the job ID is correct
- Check if you have the complete job ID
- If job is old, you may need to re-run the task
"""
            return {
                "content": [
                    {
                        "type": "text",
                        "text": response_text
                    }
                ]
            }

        # Job is still running
        if job.status in (JobStatus.PENDING, JobStatus.RUNNING):
            response_text = f"""## Job Running ⏳

**Job ID:** `{job.job_id}`
**Status:** {job.status.value}
**Started:** {job.started_at.strftime('%Y-%m-%d %H:%M:%S') if job.started_at else 'N/A'}

### Request
{job.request}

### Status
The task is currently executing. This may take a few moments depending on the complexity of the operation.

### Check Again
Re-run this tool with the same job ID to get updated status.
"""
            return {
                "content": [
                    {
                        "type": "text",
                        "text": response_text
                    }
                ]
            }

        # Job completed successfully
        if job.status == JobStatus.COMPLETED:
            response_text = f"""## Job Completed ✓

**Job ID:** `{job.job_id}`
**Started:** {job.started_at.strftime('%Y-%m-%d %H:%M:%S') if job.started_at else 'N/A'}
**Completed:** {job.completed_at.strftime('%Y-%m-%d %H:%M:%S') if job.completed_at else 'N/A'}

### Request
{job.request}

---

### Results

{job.output}
"""
            return {
                "content": [
                    {
                        "type": "text",
                        "text": response_text
                    }
                ]
            }

        # Job failed
        if job.status == JobStatus.FAILED:
            response_text = f"""## Job Failed ❌

**Job ID:** `{job.job_id}`
**Started:** {job.started_at.strftime('%Y-%m-%d %H:%M:%S') if job.started_at else 'N/A'}
**Failed:** {job.completed_at.strftime('%Y-%m-%d %H:%M:%S') if job.completed_at else 'N/A'}

### Request
{job.request}

### Error
```
{job.error or 'Unknown error occurred'}
```

### Troubleshooting
- Review the error message above
- Check Docker daemon status
- Verify Portainer connectivity
- Ensure proper permissions
- Try running the task again with `docker_execute_async`
"""
            return {
                "content": [
                    {
                        "type": "text",
                        "text": response_text
                    }
                ]
            }

        # Unknown status (shouldn't happen)
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Unknown job status: {job.status}"
                }
            ]
        }

    async def _execute_background_job(self, job_id: str, request: str):
        """
        Execute job in background and update status

        Args:
            job_id: Job ID to track
            request: User's request
        """
        try:
            # Update to running
            self.job_tracker.update_job_status(job_id, JobStatus.RUNNING)

            # Execute via Claude Code
            result = await self.executor.execute_async(request, job_id)

            # Update to completed
            self.job_tracker.update_job_status(
                job_id,
                JobStatus.COMPLETED,
                output=result
            )

        except Exception as e:
            # Update to failed
            self.job_tracker.update_job_status(
                job_id,
                JobStatus.FAILED,
                error=str(e)
            )

    def validate_environment(self) -> tuple[bool, str]:
        """
        Validate Docker management environment

        Returns:
            Tuple of (is_valid, error_message)
        """
        return self.executor.validate_environment()
