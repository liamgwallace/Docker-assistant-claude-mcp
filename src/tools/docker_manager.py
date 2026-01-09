"""
Docker management tool handlers for MCP server
Provides three tools: docker_execute, docker_execute_async, docker_job_status
"""
import asyncio
from typing import Dict, Any, Optional

from src.tools.claude_code_executor import ClaudeCodeExecutor
from src.tools.job_tracker import JobTracker, JobStatus


class DockerManager:
    """Manages Docker operations through Claude Code CLI"""

    def __init__(self):
        self.executor = ClaudeCodeExecutor()
        self.job_tracker = JobTracker()

    async def docker_execute(
        self,
        request: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute Docker/Portainer management task synchronously
        Waits for task completion and returns full output

        Args:
            request: User's natural language request for Docker management
            session_id: Optional Claude session ID to resume a conversation

        Returns:
            Tool response with markdown content and session_id
        """
        # Execute synchronously via Claude Code
        result = await self.executor.execute_sync(request, session_id=session_id)

        response = {
            "content": [
                {
                    "type": "text",
                    "text": result.content
                }
            ]
        }

        # Include session_id for conversation continuation
        if result.session_id:
            response["session_id"] = result.session_id

        return response

    async def docker_execute_async(
        self,
        request: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute Docker management task asynchronously in background
        Returns immediately with job ID

        Args:
            request: User's natural language request for Docker management
            session_id: Optional Claude session ID to resume a conversation

        Returns:
            Tool response with job ID
        """
        # Create job with optional session_id for resumption
        job = self.job_tracker.create_job(request, input_session_id=session_id)

        # Start background task with session_id
        asyncio.create_task(
            self._execute_background_job(job.job_id, request, session_id=session_id)
        )

        # Build response text
        session_info = ""
        if session_id:
            session_info = f"\n**Resuming Session:** `{session_id}`\n"

        response_text = f"""## Task Started in Background

**Job ID:** `{job.job_id}`{session_info}

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
- **completed**: Task finished successfully (includes session_id for follow-up)
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
            Tool response with job status, output, and session_id (when completed)
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
            session_info = ""
            if job.input_session_id:
                session_info = f"\n**Resuming Session:** `{job.input_session_id}`"

            response_text = f"""## Job Running ⏳

**Job ID:** `{job.job_id}`
**Status:** {job.status.value}
**Started:** {job.started_at.strftime('%Y-%m-%d %H:%M:%S') if job.started_at else 'N/A'}{session_info}

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
            session_info = ""
            if job.output_session_id:
                session_info = f"\n**Session ID:** `{job.output_session_id}` (use to continue conversation)"

            response_text = f"""## Job Completed ✓

**Job ID:** `{job.job_id}`
**Started:** {job.started_at.strftime('%Y-%m-%d %H:%M:%S') if job.started_at else 'N/A'}
**Completed:** {job.completed_at.strftime('%Y-%m-%d %H:%M:%S') if job.completed_at else 'N/A'}{session_info}

### Request
{job.request}

---

### Results

{job.output}
"""
            response = {
                "content": [
                    {
                        "type": "text",
                        "text": response_text
                    }
                ]
            }

            # Include session_id for conversation continuation
            if job.output_session_id:
                response["session_id"] = job.output_session_id

            return response

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

    async def _execute_background_job(
        self,
        job_id: str,
        request: str,
        session_id: Optional[str] = None
    ):
        """
        Execute job in background and update status

        Args:
            job_id: Job ID to track
            request: User's request
            session_id: Optional Claude session ID to resume
        """
        try:
            # Update to running
            self.job_tracker.update_job_status(job_id, JobStatus.RUNNING)

            # Execute via Claude Code with session support
            result = await self.executor.execute_async(
                request,
                job_id,
                session_id=session_id
            )

            # Update to completed with session_id from response
            self.job_tracker.update_job_status(
                job_id,
                JobStatus.COMPLETED,
                output=result.content,
                output_session_id=result.session_id
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
