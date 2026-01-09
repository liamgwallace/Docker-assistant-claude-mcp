"""
Docker Management MCP Server
FastMCP server providing AI-assisted Docker container management
"""
import asyncio
import logging
from contextlib import asynccontextmanager

from fastmcp import FastMCP
from pydantic import Field
from typing import Optional

from src.tools.docker_manager import DockerManager
from src.tools.job_tracker import JobTracker
from src.config.environment import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Docker manager
docker_manager = DockerManager()
job_tracker = JobTracker()


@asynccontextmanager
async def lifespan(app):
    """Lifespan context manager for startup and shutdown tasks"""
    # Startup
    logger.info("Starting Docker Management MCP Server")

    # Validate environment
    is_valid, message = docker_manager.validate_environment()
    if not is_valid:
        logger.warning(f"Environment validation failed: {message}")
    else:
        logger.info("Environment validated successfully")

    # Start background job cleanup task
    cleanup_task = asyncio.create_task(periodic_job_cleanup())

    yield

    # Shutdown
    logger.info("Shutting down Docker Management MCP Server")
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass


# Initialize FastMCP server
mcp = FastMCP("Docker Management Server")




@mcp.tool()
async def docker_execute(
    request: str = Field(
        description="User's natural language request for Docker management (e.g., 'Deploy nginx web server named my-nginx')"
    ),
    session_id: Optional[str] = Field(
        default=None,
        description="Optional Claude session ID to resume a previous conversation. Leave empty to start a new conversation. The response will include a session_id that can be used to continue the conversation."
    )
) -> dict:
    """
    Execute Docker/Portainer management tasks synchronously via Claude Code CLI.
    Waits for task completion and returns full output.

    This tool is best for:
    - Quick operations (restart, stop, start containers)
    - Status checks and health queries
    - Simple deployments
    - Tasks expected to complete in < 30 seconds

    Session Management:
    - Leave session_id empty to start a new conversation
    - Pass a previous session_id to continue an existing conversation
    - The response includes a session_id for follow-up messages

    Returns a markdown-formatted response with status, output, details, and session_id.
    """
    session_info = f" (session: {session_id})" if session_id else ""
    logger.info(f"docker_execute called with request: {request[:100]}...{session_info}")

    try:
        result = await docker_manager.docker_execute(request, session_id=session_id)
        return result
    except Exception as e:
        logger.error(f"Error in docker_execute: {e}", exc_info=True)
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"## Error\n\nAn error occurred: {str(e)}"
                }
            ]
        }


@mcp.tool()
async def docker_execute_async(
    request: str = Field(
        description="User's natural language request for Docker management to execute in background"
    ),
    session_id: Optional[str] = Field(
        default=None,
        description="Optional Claude session ID to resume a previous conversation. Leave empty to start a new conversation. The completed job will include a session_id for follow-up messages."
    )
) -> dict:
    """
    Execute Docker management tasks asynchronously in background.
    Returns immediately with a job ID for status tracking.

    This tool is best for:
    - Complex multi-service deployments
    - Long-running operations
    - Stack updates with image pulls
    - Tasks that may take > 30 seconds

    Session Management:
    - Leave session_id empty to start a new conversation
    - Pass a previous session_id to continue an existing conversation
    - When job completes, docker_job_status returns session_id for follow-up

    Returns a job ID that can be used with docker_job_status to check progress and get session_id.
    """
    session_info = f" (session: {session_id})" if session_id else ""
    logger.info(f"docker_execute_async called with request: {request[:100]}...{session_info}")

    try:
        result = await docker_manager.docker_execute_async(request, session_id=session_id)
        return result
    except Exception as e:
        logger.error(f"Error in docker_execute_async: {e}", exc_info=True)
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"## Error\n\nAn error occurred: {str(e)}"
                }
            ]
        }


@mcp.tool()
async def docker_job_status(
    job_id: str = Field(
        description="Job ID returned from docker_execute_async"
    )
) -> dict:
    """
    Check the status of an asynchronous Docker management job.

    Provides real-time status updates including:
    - Job current state (pending, running, completed, failed)
    - Execution start and completion times
    - Full output for completed jobs
    - Error messages for failed jobs
    - Session ID for completed jobs (enables conversation continuation)

    Use this tool repeatedly to poll for job completion.
    When the job completes, the response includes a session_id that can be
    passed to docker_execute or docker_execute_async to continue the conversation.
    """
    logger.info(f"docker_job_status called for job: {job_id}")

    try:
        result = await docker_manager.docker_job_status(job_id)
        return result
    except Exception as e:
        logger.error(f"Error in docker_job_status: {e}", exc_info=True)
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"## Error\n\nAn error occurred: {str(e)}"
                }
            ]
        }


async def periodic_job_cleanup():
    """Periodically clean up old completed jobs"""
    while True:
        try:
            await asyncio.sleep(settings.job_cleanup_interval_minutes * 60)
            logger.info("Running periodic job cleanup...")

            deleted_count = job_tracker.cleanup_old_jobs()
            logger.info(f"Cleaned up {deleted_count} old jobs")

        except asyncio.CancelledError:
            logger.info("Job cleanup task cancelled")
            raise
        except Exception as e:
            logger.error(f"Error in periodic job cleanup: {e}", exc_info=True)


# Health check endpoint
@mcp.tool()
async def health_check() -> dict:
    """
    Health check endpoint to verify server status and environment configuration.

    Returns:
    - Server status
    - Environment validation results
    - Configuration summary
    """
    is_valid, validation_message = docker_manager.validate_environment()

    status_text = f"""## Health Check

**Server Status:** Running ✓
**Environment Valid:** {'Yes ✓' if is_valid else 'No ❌'}

### Validation Details
{validation_message}

### Configuration
- Portainer URL: {settings.portainer_url}
- Portainer Endpoint: {settings.portainer_endpoint_id}
- Docker Socket: {settings.docker_socket_path}
- Stacks Directory: {settings.stacks_dir}
- Volumes Directory: {settings.volumes_dir}
- Jobs Directory: {settings.jobs_dir}

### Job Statistics
- Active Jobs: {len(job_tracker.list_jobs())}
- Job Cleanup Interval: {settings.job_cleanup_interval_minutes} minutes
- Max Job Age: {settings.max_job_age_hours} hours
"""

    return {
        "content": [
            {
                "type": "text",
                "text": status_text
            }
        ]
    }


if __name__ == "__main__":
    # Run the MCP server in HTTP mode by default
    logger.info(f"Starting Docker Management MCP Server on {settings.server_host}:{settings.server_port}")
    logger.info(f"HTTP mode - accessible at http://{settings.server_host}:{settings.server_port}/mcp")

    # Run with HTTP transport
    import asyncio
    asyncio.run(mcp.run_http_async(host=settings.server_host, port=settings.server_port))
