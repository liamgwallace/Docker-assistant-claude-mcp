# FastMCP Framework Reference Guide

## Table of Contents
1. [FastMCP Basics](#fastmcp-basics)
2. [Installation and Setup](#installation-and-setup)
3. [Creating MCP Tools](#creating-mcp-tools)
4. [Resources and Prompts](#resources-and-prompts)
5. [Server Configuration](#server-configuration)
6. [Transport Protocols](#transport-protocols)
7. [Error Handling and Logging](#error-handling-and-logging)
8. [Authentication and Security](#authentication-and-security)
9. [Testing and Debugging](#testing-and-debugging)
10. [Best Practices](#best-practices)
11. [Advanced Features](#advanced-features)

---

## FastMCP Basics

### What is FastMCP?

FastMCP 2.0 is an open-source Python framework designed to make building Model Context Protocol (MCP) servers and clients both simple and efficient. The Model Context Protocol (MCP) lets you build servers that expose data and functionality to LLM applications in a secure, standardized way. It's often described as **"the USB-C port for AI"** - providing a uniform way to connect LLMs to resources they can use.

### Key Features

- **Advanced MCP Patterns**: Server composition, proxying, OpenAPI/FastAPI generation, tool transformation
- **Enterprise Authentication**: Google, GitHub, WorkOS, Azure, Auth0, and more
- **Deployment Tools**: Multiple transport protocols (STDIO, SSE, HTTP)
- **Testing Utilities**: Built-in client for testing and debugging
- **Comprehensive Client Libraries**: Full-featured Python client for MCP servers

### Core Components

FastMCP 2.0 is built around three essential components:

1. **Tools**: Python functions exposed to LLMs via the MCP protocol (like POST endpoints)
2. **Resources**: Provide read-only access to data (like GET endpoints)
3. **Prompts**: Reusable, parameterized message templates that guide LLM responses

### Version Information

- **FastMCP 2.0**: Current production-ready version (actively maintained)
- **FastMCP 3.0**: In development (may include breaking changes)
- **Recommendation**: Pin your dependency to v2 using `fastmcp<3`

---

## Installation and Setup

### Requirements

- Python 3.10 or higher
- uv (Python package installer)

### Installation

```bash
# Install FastMCP via pip
pip install fastmcp

# Install with specific version constraint
pip install "fastmcp<3"
```

### Basic Server Setup

```python
from fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("Demo Server 🚀")

# Define a simple tool
@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

# Run the server
if __name__ == "__main__":
    mcp.run()
```

### Official Resources

- **GitHub Repository**: https://github.com/jlowin/fastmcp
- **Official Documentation**: https://gofastmcp.com
- **PyPI Package**: https://pypi.org/project/fastmcp/
- **LLM-Friendly Docs**: Available in llms.txt format at gofastmcp.com
- **MCP Server Access**: https://gofastmcp.com/mcp

---

## Creating MCP Tools

### Tool Definition

Tools are Python functions that LLMs can call during conversations. FastMCP handles parameter validation, type conversion, and protocol compliance automatically.

### Basic Tool Example

```python
from fastmcp import FastMCP

mcp = FastMCP("Calculator")

@mcp.tool
def multiply(x: float, y: float) -> float:
    """Multiply two numbers together"""
    return x * y
```

### Supported Parameter Types

FastMCP supports most types supported by Pydantic, including:

- **Built-in types**: `int`, `float`, `str`, `bool`, `bytes`
- **Dates and times**: `datetime`, `date`, `time`
- **Literals and Enums**: `Literal["option1", "option2"]`, custom Enums
- **Collections**: `dict`, `list`, `set`, `tuple`
- **UUIDs**: `UUID`
- **Complex Pydantic models**: Custom dataclasses and Pydantic models

### Parameter Validation Example

```python
from pydantic import BaseModel, Field
from typing import Literal

class UserQuery(BaseModel):
    query: str = Field(..., description="The search query")
    max_results: int = Field(10, ge=1, le=100, description="Maximum number of results")
    sort_by: Literal["relevance", "date"] = "relevance"

@mcp.tool
def search(params: UserQuery) -> dict:
    """Search with validated parameters"""
    # FastMCP automatically validates params against the model
    return {
        "query": params.query,
        "max_results": params.max_results,
        "sort_by": params.sort_by
    }
```

### Async vs Sync Tool Handlers

FastMCP is an **async-first framework** that seamlessly supports both asynchronous and synchronous functions.

#### Synchronous Tools

```python
@mcp.tool
def get_current_time() -> str:
    """Get the current timestamp"""
    from datetime import datetime
    return datetime.now().isoformat()
```

**Note**: Synchronous tools work seamlessly but can block the event loop during execution.

#### Asynchronous Tools (Recommended for I/O)

```python
import httpx

@mcp.tool
async def fetch_url(url: str) -> str:
    """Fetch content from a URL"""
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.text
```

**Best Practice**: Use async tools for I/O-bound operations (API calls, database queries, file operations) to keep your server responsive.

#### Concurrent Execution Warning

There's a known issue where non-async methods may not properly handle concurrent execution. When multiple executions occur concurrently, subsequent calls may not enter the method properly. Consider using async handlers for production servers.

### Return Value Formats

FastMCP automatically converts tool return values into appropriate MCP content blocks:

#### Automatic Conversion

```python
@mcp.tool
def get_user() -> dict:
    """Return user data"""
    return {"name": "John", "age": 30}  # Automatically converted to JSON

@mcp.tool
def get_message() -> str:
    """Return text message"""
    return "Hello, World!"  # Automatically converted to TextContent

@mcp.tool
def get_binary() -> bytes:
    """Return binary data"""
    return b"binary data"  # Base64 encoded and sent as BlobResourceContents
```

#### Advanced: ToolResult for Complete Control

```python
from fastmcp.tools.tool import ToolResult
from mcp.types import TextContent

@mcp.tool
def advanced_tool() -> ToolResult:
    """Return structured response with metadata"""
    return ToolResult(
        content=[TextContent(type="text", text="Human-readable summary")],
        structured_content={"data": "value", "count": 42},
        meta={"execution_time_ms": 145}
    )
```

**ToolResult Fields**:
- `content`: Traditional MCP content blocks (can be string, list of content blocks, or serializable value)
- `structured_content`: Machine-readable JSON object
- `meta`: Additional metadata about the execution

#### Automatic Structured Content Rules

FastMCP automatically creates structured outputs alongside traditional content:

- **Object-like results** (dict, Pydantic models, dataclasses): Always become structured content
- **Non-object results** (int, str, list): Only become structured content if there's an output schema
- **All results**: Always become traditional content blocks for backward compatibility

### Tool Customization

```python
@mcp.tool(
    name="custom_name",  # Override function name
    description="Custom description"  # Override docstring
)
def my_tool(param: str) -> str:
    """This docstring is overridden"""
    return f"Processed: {param}"
```

---

## Resources and Prompts

### Resources

Resources provide LLMs with read-only access to data such as files, database records, configurations, or dynamically generated content.

#### Basic Resource Example

```python
@mcp.resource("config://app")
def get_app_config() -> str:
    """Get application configuration"""
    return "app_version: 1.0.0\nenv: production"

@mcp.resource("file://logs/{log_name}")
def get_log_file(log_name: str) -> str:
    """Get contents of a log file"""
    with open(f"/var/logs/{log_name}", "r") as f:
        return f.read()
```

#### Resource URI Patterns

Resources are identified by URIs. FastMCP supports:
- Static URIs: `"config://app"`
- Dynamic URIs with parameters: `"file://logs/{log_name}"`

### Prompts

Prompts are reusable, parameterized message templates that guide LLM responses.

#### Basic Prompt Example

```python
@mcp.prompt
def code_review_prompt(code: str, language: str) -> str:
    """Generate a code review prompt"""
    return f"""Please review the following {language} code:

```{language}
{code}
```

Focus on:
1. Code quality and best practices
2. Potential bugs or issues
3. Performance considerations
4. Suggestions for improvement
"""
```

#### Prompt Customization

```python
@mcp.prompt(
    name="custom_prompt_name",
    description="Custom description for the prompt"
)
def my_prompt(param: str) -> str:
    """Generate prompt template"""
    return f"Template with {param}"
```

---

## Server Configuration

### Server Initialization

```python
from fastmcp import FastMCP

# Basic initialization
mcp = FastMCP("My Server")

# With custom configuration
mcp = FastMCP(
    "My Server",
    on_duplicate_tools="warn",      # 'error', 'warn', or 'ignore'
    on_duplicate_resources="warn",  # Handle duplicate resource names
    on_duplicate_prompts="warn"     # Handle duplicate prompt names
)
```

### Configuration Precedence

FastMCP configuration follows this precedence (highest to lowest):

1. **Keyword arguments** during initialization
2. **Environment variables** prefixed with `FASTMCP_SERVER_`
3. **Values from .env file**
4. **Default values**

### Configuration File Structure

FastMCP uses a configuration file with three main sections:

#### 1. Source Configuration (WHERE)

Defines where the server code lives:

```yaml
source:
  path: "./server.py"
  module: "my_package.server"
```

#### 2. Environment Configuration (WHAT)

Defines dependencies and environment:

```yaml
environment:
  python: "3.11"
  dependencies:
    - fastmcp
    - httpx
    - pydantic
```

#### 3. Deployment Configuration (HOW)

Controls runtime behavior:

```yaml
deployment:
  transport: "stdio"  # or "sse", "http"
  host: "127.0.0.1"
  port: 8000
  environment_variables:
    API_KEY: "${API_KEY}"
```

### Error Handling

FastMCP provides several mechanisms for error handling:

#### Tool-Level Error Handling

```python
@mcp.tool
async def risky_operation(param: str) -> str:
    """Operation that might fail"""
    try:
        # Perform operation
        result = await some_async_operation(param)
        return result
    except ValueError as e:
        # Return error message to client
        return f"Error: Invalid value - {str(e)}"
    except Exception as e:
        # Log error and return generic message
        print(f"Unexpected error: {e}")
        return "An unexpected error occurred"
```

#### Client Initialization Error Handling

```python
from fastmcp import Client

client = Client("my_mcp_server.py", auto_initialize=False)

async with client:
    try:
        # Initialize manually with custom timeout
        result = await client.initialize(timeout=10.0)
    except TimeoutError:
        print("Server initialization timed out")
    except Exception as e:
        print(f"Initialization failed: {e}")
```

#### Middleware-Based Error Handling

```python
from fastmcp.exceptions import McpError
from fastmcp.middleware import Middleware

class AuthenticationMiddleware(Middleware):
    async def on_initialize(self, context, call_next):
        credentials = context.request.get("credentials")

        if not self.is_valid(credentials):
            raise McpError(
                code=-32000,
                message="Invalid credentials",
                data={"reason": "Authentication failed"}
            )

        return await call_next(context)

# Apply middleware to server
mcp.add_middleware(AuthenticationMiddleware())
```

### Health Checks

While FastMCP doesn't have built-in health check endpoints, you can implement them when using HTTP transport:

```python
# When using FastAPI integration
from fastapi import FastAPI
from fastmcp import FastMCP

app = FastAPI()
mcp = FastMCP("My Server")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "server": "running"}

# Mount FastMCP to FastAPI
app.mount("/mcp", mcp.as_app())
```

---

## Transport Protocols

FastMCP supports three main transport protocols, each designed for specific use cases.

### STDIO Transport (Default)

STDIO is the **default transport** for FastMCP servers, perfect for command-line tools and desktop applications like Claude Desktop.

#### Usage

```python
# STDIO is the default - just call run()
mcp.run()

# Or explicitly specify
mcp.run(transport="stdio")
```

#### Characteristics

- Communicates through standard input/output streams
- Best for local, single-user applications
- No network configuration needed
- Integrated with desktop AI assistants

### SSE Transport (Server-Sent Events)

SSE was the original HTTP-based transport for MCP. While still supported, it exists mainly for backward compatibility.

#### Usage

```python
mcp.run(transport="sse", host="127.0.0.1", port=8000)
```

#### Starting Message

```
Starting MCP server
Transport: sse
Uvicorn running on http://127.0.0.1:8000
```

#### Implementation Details

- Uses Starlette for ASGI interface
- Wrapped by uvicorn server
- One-way communication from server to client
- Limited compared to newer HTTP transport

**Note**: SSE exists only for backward compatibility and shouldn't be used in new projects.

### HTTP Transport (Recommended for Production)

The modern HTTP-based transport with full bidirectional communication.

#### Usage

```python
mcp.run(transport="http", host="0.0.0.0", port=8000)
```

#### When to Use Each Transport

- **STDIO**: Building a tool for local use
- **HTTP**: Need a centralized service that multiple clients can access
- **SSE**: Only for backward compatibility with existing systems

### ASGI Deployment with Uvicorn

For production deployments, you can create an ASGI application:

```python
from fastmcp import FastMCP

mcp = FastMCP("Production Server")

# Define your tools
@mcp.tool
def my_tool() -> str:
    return "Hello"

# Create ASGI app
app = mcp.as_app()

# Run with uvicorn from command line:
# uvicorn server:app --host 0.0.0.0 --port 8000
```

**Important**: FastMCP needs a proper ASGI framework like FastAPI or Starlette to handle HTTP routing. It's not designed to be the entire ASGI application passed to Uvicorn directly.

---

## Error Handling and Logging

### Logging

FastMCP supports two types of logging:

#### 1. Client Logging

Send messages back to MCP clients for debugging:

```python
from fastmcp import Context

@mcp.tool
async def debug_tool(ctx: Context, param: str) -> str:
    """Tool with client logging"""

    # Send different log levels to client
    ctx.log.debug("Debug information")
    ctx.log.info("Processing started")
    ctx.log.warning("This is a warning")
    ctx.log.error("An error occurred")

    return "Done"
```

**Log Levels**:
- `ctx.log.debug()`: Debug messages
- `ctx.log.info()`: Informational messages
- `ctx.log.warning()`: Warning messages
- `ctx.log.error()`: Error messages

**Note**: Messages sent to clients are also logged to the server's log at DEBUG level.

#### 2. Server-Side Logging

For standard server-side logging (files, console):

```python
from fastmcp.utilities.logging import get_logger
import logging

# Get FastMCP logger
logger = get_logger(__name__)

# Or use Python's built-in logging
logger = logging.getLogger(__name__)

@mcp.tool
def logged_tool(param: str) -> str:
    """Tool with server-side logging"""
    logger.info(f"Processing param: {param}")

    try:
        result = process(param)
        logger.debug(f"Result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error processing: {e}", exc_info=True)
        raise
```

#### Enable Debug Logging

```python
import logging

# Enable debug logging for FastMCP
logging.basicConfig(level=logging.DEBUG)

# Or specifically for client messages
logging.getLogger("fastmcp.server.context.to_client").setLevel(logging.DEBUG)
```

### Common Error Patterns

#### 1. Request Timeout Error (-32001)

```python
# Client side - increase timeout
client = Client("server.py", auto_initialize=False)
async with client:
    await client.initialize(timeout=30.0)  # Increase from default
```

#### 2. Initialization Errors

```python
@mcp.tool
async def safe_init_tool() -> str:
    """Handle initialization gracefully"""
    try:
        # Initialization logic
        await setup_resources()
        return "Initialized successfully"
    except Exception as e:
        # Log and return error to client
        logger.error(f"Initialization failed: {e}")
        return f"Failed to initialize: {str(e)}"
```

#### 3. STDIO Transport Errors

If you see "Received request before initialization was complete":

```python
# Ensure proper initialization sequence
from fastmcp import FastMCP

mcp = FastMCP("My Server")

# Define all tools/resources first
@mcp.tool
def my_tool() -> str:
    return "Hello"

# Then run
if __name__ == "__main__":
    mcp.run()  # Properly waits for initialization
```

### Best Practices for Error Handling

1. **Implement retry logic** for external services:
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def fetch_external_data(url: str):
    """Fetch with automatic retries"""
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()
```

2. **Use context managers** for resource cleanup:
```python
@mcp.tool
async def database_query(query: str) -> dict:
    """Query with proper resource management"""
    async with get_db_connection() as conn:
        result = await conn.execute(query)
        return result
```

3. **Log errors to server, return user-friendly messages to client**:
```python
@mcp.tool
async def user_facing_tool(ctx: Context, param: str) -> str:
    """Handle errors gracefully"""
    try:
        result = await complex_operation(param)
        return result
    except ValueError as e:
        # User error - return helpful message
        ctx.log.warning(f"Invalid input: {e}")
        return f"Invalid input: {str(e)}"
    except Exception as e:
        # System error - log details, return generic message
        logger.error(f"Unexpected error: {e}", exc_info=True)
        ctx.log.error("An unexpected error occurred")
        return "An unexpected error occurred. Please try again."
```

---

## Authentication and Security

### Authentication Patterns

FastMCP supports multiple authentication patterns for securing your MCP server.

#### 1. Session-Based Authentication

```python
from fastmcp import FastMCP, Context

async def authenticate(request):
    """Authenticate incoming requests"""
    token = request.headers.get("Authorization")

    if not validate_token(token):
        raise ValueError("Invalid authentication token")

    # Return authentication context
    return {"user_id": extract_user_id(token)}

mcp = FastMCP("Secure Server", authenticate=authenticate)

@mcp.tool
async def secure_tool(ctx: Context) -> str:
    """Access authentication context"""
    user_id = ctx.request_context.get("user_id")
    return f"Hello, user {user_id}"
```

#### 2. OAuth Proxy Architecture

FastMCP includes built-in OAuth 2.1 support with complete flow handling:

**Features**:
- Dynamic Client Registration (DCR)
- PKCE (Proof Key for Code Exchange)
- Consent management
- Token management with encryption

```python
from fastmcp.auth import OAuthProvider

# Configure OAuth provider
oauth = OAuthProvider(
    client_id="your_client_id",
    client_secret="your_client_secret",
    authorization_url="https://provider.com/oauth/authorize",
    token_url="https://provider.com/oauth/token"
)

mcp = FastMCP("OAuth Server", auth_provider=oauth)
```

#### 3. JWT Token Validation

For servers acting as resource servers:

```python
import jwt
from fastmcp import FastMCP

async def validate_jwt(request):
    """Validate JWT tokens"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")

    try:
        payload = jwt.decode(
            token,
            key="your_public_key",
            algorithms=["RS256"],
            audience="your_api"
        )
        return payload
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")

mcp = FastMCP("JWT Server", authenticate=validate_jwt)
```

### Security Best Practices

#### 1. Validate All Inputs

```python
from pydantic import BaseModel, Field, validator

class SecureInput(BaseModel):
    user_input: str = Field(..., max_length=1000)

    @validator('user_input')
    def sanitize_input(cls, v):
        # Remove potentially dangerous characters
        return v.replace("<", "&lt;").replace(">", "&gt;")

@mcp.tool
def secure_tool(params: SecureInput) -> str:
    """Tool with input validation"""
    return f"Processed: {params.user_input}"
```

#### 2. Implement Rate Limiting

```python
from collections import defaultdict
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, max_requests=100, window_seconds=60):
        self.max_requests = max_requests
        self.window = timedelta(seconds=window_seconds)
        self.requests = defaultdict(list)

    def is_allowed(self, user_id: str) -> bool:
        now = datetime.now()
        cutoff = now - self.window

        # Clean old requests
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if req_time > cutoff
        ]

        # Check limit
        if len(self.requests[user_id]) >= self.max_requests:
            return False

        self.requests[user_id].append(now)
        return True

rate_limiter = RateLimiter()

@mcp.tool
async def rate_limited_tool(ctx: Context) -> str:
    """Tool with rate limiting"""
    user_id = ctx.request_context.get("user_id", "anonymous")

    if not rate_limiter.is_allowed(user_id):
        raise ValueError("Rate limit exceeded")

    return "Success"
```

#### 3. Secure External API Calls

```python
import os
from typing import Optional

@mcp.tool
async def call_external_api(endpoint: str) -> dict:
    """Securely call external APIs"""
    # Use environment variables for secrets
    api_key = os.getenv("EXTERNAL_API_KEY")

    if not api_key:
        raise ValueError("API key not configured")

    # Validate endpoint whitelist
    allowed_endpoints = [
        "https://api.example.com/v1/users",
        "https://api.example.com/v1/data"
    ]

    if endpoint not in allowed_endpoints:
        raise ValueError("Endpoint not allowed")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            endpoint,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10.0
        )
        response.raise_for_status()
        return response.json()
```

### Known Security Issues (Resolved)

FastMCP's OAuth implementation has been battle-tested, and two MCP-specific vulnerabilities were responsibly disclosed and addressed:

1. **Confused Deputy Attack**: Fixed in early 2025
2. **Token Security Issue**: Patched with encryption improvements

Always use the latest version of FastMCP for security updates.

---

## Testing and Debugging

### Testing with FastMCP Client

FastMCP includes a built-in client for testing servers without connecting to an AI assistant.

#### In-Memory Testing

```python
import asyncio
from fastmcp import FastMCP, Client
from fastmcp.transport import FastMCPTransport

# Define your server
mcp = FastMCP("Test Server")

@mcp.tool
def add(a: int, b: int) -> int:
    return a + b

# Test the server
async def test_server():
    # Connect directly via in-memory transport
    async with Client(mcp) as client:
        # List available tools
        tools = await client.list_tools()
        print(f"Available tools: {[t.name for t in tools]}")

        # Call a tool
        result = await client.call_tool("add", {"a": 5, "b": 3})
        print(f"Result: {result}")

        assert result == 8, "Test failed"

asyncio.run(test_server())
```

#### Testing with External Server

```python
from fastmcp import Client

async def test_external_server():
    # Connect to server process
    client = Client("path/to/server.py")

    async with client:
        # Initialize
        await client.initialize(timeout=10.0)

        # Test tools
        result = await client.call_tool("my_tool", {"param": "value"})
        assert result is not None
```

### Unit Testing with pytest

```python
import pytest
from fastmcp import FastMCP, Client

@pytest.fixture
def mcp_server():
    """Create test server"""
    mcp = FastMCP("Test")

    @mcp.tool
    def test_tool(value: str) -> str:
        return f"processed: {value}"

    return mcp

@pytest.mark.asyncio
async def test_tool_execution(mcp_server):
    """Test tool execution"""
    async with Client(mcp_server) as client:
        result = await client.call_tool("test_tool", {"value": "test"})
        assert result == "processed: test"

@pytest.mark.asyncio
async def test_tool_error_handling(mcp_server):
    """Test error handling"""
    async with Client(mcp_server) as client:
        with pytest.raises(ValueError):
            await client.call_tool("nonexistent_tool", {})
```

### Debugging with MCP Inspector

The **MCP Inspector** provides a Web UI for testing and debugging your server.

#### Installation

```bash
pip install "fastmcp[cli]"
```

#### Usage

```bash
# Run with MCP Inspector
fastmcp dev server.py

# Or for TypeScript
npx fastmcp dev server.ts
```

**Features**:
- Interactive tool testing
- Real-time request/response inspection
- Parameter validation testing
- Resource browsing
- Prompt template testing

### Development Mode

```bash
# Run server in development mode with auto-reload
fastmcp dev --reload server.py

# With specific transport
fastmcp dev --transport sse --port 8000 server.py
```

### Debugging Tips

#### 1. Enable Verbose Logging

```python
import logging

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Enable FastMCP debug logs
logging.getLogger("fastmcp").setLevel(logging.DEBUG)
```

#### 2. Use Print Debugging (STDIO only)

```python
import sys

@mcp.tool
def debug_tool(param: str) -> str:
    # Print to stderr (stdout is used for protocol)
    print(f"Debug: processing {param}", file=sys.stderr)
    return f"processed: {param}"
```

#### 3. Inspect Context

```python
from fastmcp import Context

@mcp.tool
async def inspect_context(ctx: Context) -> dict:
    """Inspect request context"""
    return {
        "request_id": ctx.request_id,
        "session_info": str(ctx.session),
        "request_context": ctx.request_context
    }
```

#### 4. Test Individual Functions

```python
# Your tool
@mcp.tool
def my_tool(param: str) -> str:
    return process_data(param)

# Test the underlying function directly
def test_process_data():
    result = process_data("test")
    assert result == "expected_output"
```

---

## Best Practices

### Project Structure

#### Recommended Directory Structure

```
my-mcp-server/
├── .env                    # Environment variables
├── pyproject.toml          # Project dependencies
├── README.md              # Documentation
├── server.py              # Main server file
├── config/
│   └── settings.py        # Configuration management
├── tools/
│   ├── __init__.py
│   ├── database.py        # Database tools
│   ├── api.py            # API tools
│   └── file_ops.py       # File operation tools
├── resources/
│   ├── __init__.py
│   └── data.py           # Resource definitions
├── prompts/
│   ├── __init__.py
│   └── templates.py      # Prompt templates
├── utils/
│   ├── __init__.py
│   ├── auth.py           # Authentication utilities
│   └── logging.py        # Logging setup
└── tests/
    ├── __init__.py
    ├── test_tools.py
    ├── test_resources.py
    └── test_integration.py
```

#### Modular Server Setup

```python
# server.py
from fastmcp import FastMCP
from tools import database, api, file_ops
from resources import data
from prompts import templates
from config.settings import get_settings

settings = get_settings()
mcp = FastMCP(settings.server_name)

# Register tools from modules
database.register_tools(mcp)
api.register_tools(mcp)
file_ops.register_tools(mcp)

# Register resources
data.register_resources(mcp)

# Register prompts
templates.register_prompts(mcp)

if __name__ == "__main__":
    mcp.run()
```

```python
# tools/database.py
def register_tools(mcp):
    @mcp.tool
    def query_db(sql: str) -> dict:
        """Execute database query"""
        # Implementation
        pass

    @mcp.tool
    async def async_query_db(sql: str) -> dict:
        """Execute async database query"""
        # Implementation
        pass
```

### Context Management

#### Using Context for Request Data

```python
from fastmcp import Context

@mcp.tool
async def context_aware_tool(ctx: Context, param: str) -> str:
    """Tool that uses context"""

    # Access request ID
    request_id = ctx.request_id

    # Access authentication data
    user_id = ctx.request_context.get("user_id")

    # Send log to client
    ctx.log.info(f"Processing request {request_id} for user {user_id}")

    # Use session data
    session_data = ctx.session

    return f"Processed for user {user_id}"
```

#### Lifespan Context Management

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def app_lifespan():
    """Manage application lifespan"""
    # Startup
    db = await connect_to_database()
    cache = await initialize_cache()

    try:
        yield {"db": db, "cache": cache}
    finally:
        # Shutdown
        await db.close()
        await cache.close()

# Use with server
mcp = FastMCP("My Server", lifespan=app_lifespan)

@mcp.tool
async def db_tool(ctx: Context) -> dict:
    """Access lifespan resources"""
    db = ctx.lifespan_resources.get("db")
    result = await db.query("SELECT * FROM users")
    return result
```

### Tool Response Formats

#### 1. Simple Responses

```python
@mcp.tool
def simple_tool() -> str:
    """Return simple string"""
    return "Hello, World!"
```

#### 2. Structured Data

```python
from pydantic import BaseModel

class UserData(BaseModel):
    id: int
    name: str
    email: str

@mcp.tool
def get_user(user_id: int) -> UserData:
    """Return structured user data"""
    return UserData(
        id=user_id,
        name="John Doe",
        email="john@example.com"
    )
```

#### 3. Rich Responses with Metadata

```python
from fastmcp.tools.tool import ToolResult

@mcp.tool
async def rich_response_tool(query: str) -> ToolResult:
    """Return response with metadata"""
    import time

    start = time.time()
    result = await process_query(query)
    duration = time.time() - start

    return ToolResult(
        content=f"Query processed: {query}",
        structured_content={
            "query": query,
            "results": result,
            "count": len(result)
        },
        meta={
            "execution_time_ms": int(duration * 1000),
            "cache_hit": False
        }
    )
```

### Error Handling Patterns

#### 1. Graceful Degradation

```python
@mcp.tool
async def resilient_tool(url: str) -> dict:
    """Tool with fallback behavior"""
    try:
        # Try primary method
        return await fetch_from_api(url)
    except httpx.HTTPError:
        # Fall back to cache
        cached = get_from_cache(url)
        if cached:
            return {"data": cached, "source": "cache"}
        raise ValueError("Service unavailable and no cache available")
```

#### 2. User-Friendly Error Messages

```python
@mcp.tool
def user_friendly_tool(email: str) -> str:
    """Return helpful error messages"""
    if not "@" in email:
        return "Error: Please provide a valid email address with @ symbol"

    if not email.endswith((".com", ".org", ".net")):
        return "Error: Email domain must end with .com, .org, or .net"

    return f"Email {email} is valid"
```

#### 3. Detailed Logging for Debugging

```python
import logging

logger = logging.getLogger(__name__)

@mcp.tool
async def well_logged_tool(ctx: Context, data: dict) -> dict:
    """Tool with comprehensive logging"""
    logger.info(f"Tool called with data: {data}")
    ctx.log.info("Processing started")

    try:
        result = await process(data)
        logger.debug(f"Processing successful: {result}")
        ctx.log.info("Processing completed")
        return result
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        ctx.log.warning(f"Invalid input: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        ctx.log.error("An unexpected error occurred")
        raise
```

### Performance Optimization

#### 1. Use Async for I/O Operations

```python
import httpx

@mcp.tool
async def optimized_api_call(urls: list[str]) -> list[dict]:
    """Make concurrent API calls"""
    async with httpx.AsyncClient() as client:
        tasks = [client.get(url) for url in urls]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        results = []
        for resp in responses:
            if isinstance(resp, Exception):
                results.append({"error": str(resp)})
            else:
                results.append(resp.json())

        return results
```

#### 2. Implement Caching

```python
from functools import lru_cache
from datetime import datetime, timedelta

class CacheWithExpiry:
    def __init__(self, ttl_seconds=300):
        self.cache = {}
        self.ttl = timedelta(seconds=ttl_seconds)

    def get(self, key):
        if key in self.cache:
            value, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.ttl:
                return value
            del self.cache[key]
        return None

    def set(self, key, value):
        self.cache[key] = (value, datetime.now())

cache = CacheWithExpiry()

@mcp.tool
async def cached_tool(query: str) -> dict:
    """Tool with caching"""
    # Check cache
    cached = cache.get(query)
    if cached:
        return {"data": cached, "cached": True}

    # Fetch fresh data
    result = await expensive_operation(query)
    cache.set(query, result)

    return {"data": result, "cached": False}
```

#### 3. Stream Large Responses

```python
@mcp.tool
async def stream_large_file(filepath: str) -> str:
    """Stream large file content"""
    chunks = []
    chunk_size = 1024 * 1024  # 1MB chunks

    with open(filepath, 'r') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            chunks.append(chunk)

    return ''.join(chunks)
```

### Security Best Practices

1. **Never hardcode secrets**
```python
import os

API_KEY = os.getenv("API_KEY")  # Good
# API_KEY = "sk-1234..."  # Bad
```

2. **Validate and sanitize inputs**
```python
from pydantic import BaseModel, validator

class SafeInput(BaseModel):
    user_input: str

    @validator('user_input')
    def sanitize(cls, v):
        # Remove dangerous patterns
        return v.replace("'; DROP TABLE", "")
```

3. **Use HTTPS for external calls**
```python
@mcp.tool
async def secure_api_call(endpoint: str) -> dict:
    if not endpoint.startswith("https://"):
        raise ValueError("Only HTTPS endpoints allowed")

    async with httpx.AsyncClient(verify=True) as client:
        return await client.get(endpoint)
```

4. **Implement request timeouts**
```python
@mcp.tool
async def timeout_protected(url: str) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        return await client.get(url)
```

---

## Advanced Features

### Server Composition

Mount multiple FastMCP servers into a single application:

```python
from fastmcp import FastMCP

# Create sub-servers
db_server = FastMCP("Database")
api_server = FastMCP("API")

@db_server.tool
def query_db(sql: str) -> dict:
    return {"result": "data"}

@api_server.tool
async def fetch_data(url: str) -> dict:
    return {"data": "value"}

# Create main server and mount sub-servers
main_server = FastMCP("Main Server")
main_server.mount("/db", db_server)
main_server.mount("/api", api_server)

# Now all tools are available under main server
main_server.run()
```

### FastAPI Integration

Integrate FastMCP with FastAPI for advanced HTTP features:

```python
from fastapi import FastAPI
from fastmcp import FastMCP

app = FastAPI()
mcp = FastMCP("My MCP Server")

@mcp.tool
def my_tool(param: str) -> str:
    return f"processed: {param}"

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/metrics")
async def metrics():
    return {"tools_count": len(mcp.list_tools())}

# Mount FastMCP to FastAPI
app.mount("/mcp", mcp.as_app())

# Run with: uvicorn server:app
```

### OpenAPI Generation

FastMCP can generate OpenAPI specifications from your MCP tools:

```python
from fastmcp import FastMCP

mcp = FastMCP("API Server")

@mcp.tool
def calculate(a: int, b: int, operation: str) -> int:
    """Perform calculation on two numbers"""
    if operation == "add":
        return a + b
    elif operation == "multiply":
        return a * b
    raise ValueError(f"Unknown operation: {operation}")

# Generate OpenAPI spec
openapi_spec = mcp.to_openapi()
print(openapi_spec)
```

### Tool Transformation

Transform and adapt tools dynamically:

```python
from fastmcp import FastMCP

mcp = FastMCP("Transform Server")

@mcp.tool
def original_tool(value: str) -> str:
    return value.upper()

# Create transformed version
@mcp.tool(name="prefixed_tool")
def transformed_tool(value: str) -> str:
    """Transformed version with prefix"""
    result = original_tool(value)
    return f"PREFIX_{result}"
```

### Proxying

Allow one FastMCP server to act as a frontend for another:

```python
from fastmcp import FastMCP, Client

# Backend server
backend = FastMCP("Backend")

@backend.tool
def backend_tool() -> str:
    return "Backend result"

# Proxy server
proxy = FastMCP("Proxy")

@proxy.tool
async def proxy_tool() -> str:
    """Call backend through proxy"""
    async with Client(backend) as client:
        result = await client.call_tool("backend_tool", {})
        return f"Proxied: {result}"

proxy.run()
```

### Dependency Injection

Use context for dependency injection:

```python
from fastmcp import FastMCP, Context
from contextlib import asynccontextmanager

class DatabaseService:
    async def query(self, sql: str):
        return {"result": "data"}

@asynccontextmanager
async def lifespan():
    db = DatabaseService()
    yield {"db": db}

mcp = FastMCP("DI Server", lifespan=lifespan)

@mcp.tool
async def query_tool(ctx: Context, sql: str) -> dict:
    """Tool using injected dependency"""
    db = ctx.lifespan_resources.get("db")
    return await db.query(sql)
```

---

## Summary

FastMCP is a powerful, production-ready framework for building MCP servers in Python. Key takeaways:

- **Easy to Start**: Simple decorator-based API for defining tools, resources, and prompts
- **Flexible**: Multiple transport protocols (STDIO, SSE, HTTP) for different deployment scenarios
- **Type-Safe**: Full Pydantic integration for parameter validation and type checking
- **Async-First**: Seamless support for both sync and async operations
- **Production-Ready**: Built-in authentication, logging, error handling, and testing utilities
- **Extensible**: Server composition, FastAPI integration, and advanced features

### Quick Reference

```python
from fastmcp import FastMCP, Context
from pydantic import BaseModel

# Initialize server
mcp = FastMCP("My Server")

# Define a tool
@mcp.tool
async def my_tool(ctx: Context, param: str) -> dict:
    """Tool description"""
    ctx.log.info("Processing...")
    return {"result": param}

# Define a resource
@mcp.resource("data://{name}")
def get_data(name: str) -> str:
    """Resource description"""
    return f"Data for {name}"

# Define a prompt
@mcp.prompt
def my_prompt(topic: str) -> str:
    """Prompt description"""
    return f"Write about: {topic}"

# Run server
if __name__ == "__main__":
    mcp.run()  # STDIO by default
    # mcp.run(transport="http", port=8000)  # HTTP
```

### Additional Resources

- **Official Documentation**: https://gofastmcp.com
- **GitHub Repository**: https://github.com/jlowin/fastmcp
- **Community Examples**: https://github.com/JoshuaWink/fastmcp-templates
- **MCP Protocol Specification**: https://modelcontextprotocol.io
- **Python SDK**: https://github.com/modelcontextprotocol/python-sdk

---

## License

FastMCP is open-source software. Check the [GitHub repository](https://github.com/jlowin/fastmcp) for license information.

## Contributing

Contributions are welcome! Visit the [FastMCP GitHub repository](https://github.com/jlowin/fastmcp) to:
- Report issues
- Submit pull requests
- Request features
- Join discussions

---

*Last Updated: January 2026*
