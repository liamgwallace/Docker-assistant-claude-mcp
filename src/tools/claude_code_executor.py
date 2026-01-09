"""
Claude Code CLI wrapper for executing Docker management tasks
"""
import asyncio
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import yaml
import os

from src.config.environment import settings


@dataclass
class ExecutionResult:
    """Result from Claude Code CLI execution"""
    content: str  # The response content (markdown)
    session_id: Optional[str] = None  # Claude session ID for continuation
    is_error: bool = False  # Whether this is an error response


class ClaudeCodeExecutor:
    """Executes Docker management tasks via Claude Code CLI"""

    def __init__(self):
        self.cli_path = settings.claude_code_cli_path
        self.skill_file = settings.skills_dir / "docker-management-skill.md"
        self.config_file = settings.config_dir / "system_config.yaml"
        self.template_file = settings.config_dir / "docker_compose_template.yaml"

    def _load_skill_content(self) -> str:
        """Load the Docker management skill file content"""
        try:
            with open(self.skill_file, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return "# Docker Management Skill\n\n[Skill file not found - using default context]"

    def _load_system_config(self) -> str:
        """Load system configuration as YAML string"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            return yaml.dump(config_data, default_flow_style=False)
        except FileNotFoundError:
            return "# System configuration not found"

    def _load_template(self) -> str:
        """Load Docker Compose template"""
        try:
            with open(self.template_file, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return "# Template not found"

    def _build_prompt(self, user_request: str) -> str:
        """
        Build comprehensive prompt for Claude Code

        Args:
            user_request: User's Docker management request

        Returns:
            Complete prompt with context
        """
        skill_content = self._load_skill_content()
        system_config = self._load_system_config()
        template = self._load_template()

        prompt = f"""# Docker Management Task

## Context and Capabilities

You are managing a Docker environment with full access to:
- Docker CLI (direct access to Docker daemon)
- Portainer CLI tools (psu and portainer-cli)
- File system access to stacks and volumes directories

{skill_content}

---

## System Configuration

```yaml
{system_config}
```

---

## Docker Compose Template Reference

```yaml
{template}
```

---

## User Request

{user_request}

---

## Instructions

1. Analyze the user request carefully
2. Determine what Docker/Portainer commands are needed
3. Execute the necessary commands
4. Provide a clear response in markdown format with:
   - **Status** section indicating success/failure
   - **Output** section with relevant command outputs
   - **Details** section with what was done
   - **Next Steps** if applicable (optional)

5. If deploying new stacks:
   - Follow the template structure
   - Apply correct Traefik labels if web service
   - Ensure external 'web' network is used
   - Save compose files to correct directories
   - Check for port conflicts

6. If checking status or health:
   - Provide clear, actionable information
   - Include container states, health checks, and logs if relevant

7. If errors occur:
   - Explain what went wrong
   - Suggest possible solutions
   - Include error messages

Execute this task now and provide your response in markdown format.
"""

        return prompt

    async def execute_sync(
        self,
        user_request: str,
        session_id: Optional[str] = None
    ) -> ExecutionResult:
        """
        Execute Docker management task synchronously via Claude Code

        Args:
            user_request: User's natural language request
            session_id: Optional session ID to resume a conversation

        Returns:
            ExecutionResult with content and session_id
        """
        prompt = self._build_prompt(user_request)

        try:
            # Build command arguments
            cmd_args = [
                self.cli_path,
                "-p",  # Print mode for non-interactive execution
                "--dangerously-skip-permissions",
                "--model", settings.claude_model,
                "--output-format", "json",  # Get JSON output with session_id
            ]

            # Add --resume flag if we have a session_id to continue
            if session_id:
                cmd_args.extend(["--resume", session_id])

            # Create environment with IS_SANDBOX=1
            env = os.environ.copy()  # Copy current environment
            env['IS_SANDBOX'] = '1'  # Add IS_SANDBOX=1
                        
            # Execute Claude Code CLI with the prompt
            process = await asyncio.create_subprocess_exec(
                *cmd_args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            # Send prompt via stdin and get response
            stdout, stderr = await process.communicate(input=prompt.encode('utf-8'))

            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                return ExecutionResult(
                    content=f"""## Status: Failed ❌

### Error
Claude Code execution failed with return code {process.returncode}

### Error Details
```
{error_msg}
```

### Troubleshooting
- Verify Claude Code CLI is installed and in PATH
- Check ANTHROPIC_API_KEY is set correctly
- Review the error message above for specific issues
""",
                    is_error=True
                )

            # Parse JSON response to extract session_id and content
            raw_output = stdout.decode()
            return self._parse_json_response(raw_output)

        except FileNotFoundError:
            return ExecutionResult(
                content=f"""## Status: Failed ❌

### Error
Claude Code CLI not found at path: `{self.cli_path}`

### Solution
1. Install Claude Code CLI
2. Ensure it's in your system PATH
3. Or set CLAUDE_CODE_CLI_PATH environment variable to the correct path

### Installation
Visit: https://github.com/anthropics/claude-code for installation instructions
""",
                is_error=True
            )

        except Exception as e:
            return ExecutionResult(
                content=f"""## Status: Failed ❌

### Error
Unexpected error executing Claude Code CLI

### Details
```
{str(e)}
```

### Troubleshooting
- Check logs for detailed error information
- Verify all dependencies are installed
- Ensure proper permissions for Docker socket access
""",
                is_error=True
            )

    def _parse_json_response(self, raw_output: str) -> ExecutionResult:
        """
        Parse JSON response from Claude Code CLI

        Args:
            raw_output: Raw stdout from Claude CLI

        Returns:
            ExecutionResult with parsed content and session_id
        """
        try:
            response_data = json.loads(raw_output)

            # Extract content - try various possible keys
            content = (
                response_data.get("result") or
                response_data.get("content") or
                raw_output
            )

            # If content is a list (MCP format), extract text
            if isinstance(content, list):
                text_parts = []
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        text_parts.append(item.get("text", ""))
                content = "\n".join(text_parts) if text_parts else str(content)

            # Extract session ID
            session_id = response_data.get("session_id")

            return ExecutionResult(
                content=content,
                session_id=session_id,
                is_error=False
            )

        except json.JSONDecodeError:
            # If JSON parsing fails, return raw output (fallback for non-JSON responses)
            return ExecutionResult(
                content=raw_output,
                session_id=None,
                is_error=False
            )

    async def execute_async(
        self,
        user_request: str,
        job_id: str,
        session_id: Optional[str] = None
    ) -> ExecutionResult:
        """
        Execute Docker management task asynchronously
        This is a wrapper around execute_sync for background execution

        Args:
            user_request: User's natural language request
            job_id: Job ID for tracking
            session_id: Optional session ID to resume a conversation

        Returns:
            ExecutionResult with content and session_id
        """
        # For async execution, we just call the sync version with session support
        # The async behavior is handled by the job tracker
        return await self.execute_sync(user_request, session_id=session_id)

    def validate_environment(self) -> tuple[bool, str]:
        """
        Validate that the execution environment is properly configured

        Returns:
            Tuple of (is_valid, error_message)
        """
        errors = []

        # Check Claude Code CLI exists
        try:
            result = subprocess.run(
                [self.cli_path, "-v"],  # Use -v instead of --version
                capture_output=True,
                timeout=5,
                text=True
            )
            if result.returncode != 0:
                errors.append(f"Claude Code CLI returned error: {result.stderr}")
        except FileNotFoundError:
            errors.append(f"Claude Code CLI not found at: {self.cli_path}")
        except Exception as e:
            errors.append(f"Error checking Claude Code CLI: {str(e)}")

        # Check skill file exists
        if not self.skill_file.exists():
            errors.append(f"Skill file not found at: {self.skill_file}")

        # Check Docker socket access
        docker_socket = Path(settings.docker_socket_path)
        if not docker_socket.exists():
            errors.append(f"Docker socket not found at: {settings.docker_socket_path}")

        # Check API key
        if not settings.anthropic_api_key:
            errors.append("ANTHROPIC_API_KEY not set")

        if errors:
            return False, "\n".join(errors)

        return True, "Environment validated successfully"
