# Agent Context for IncrediBuild MCP Server

This document provides context for AI agents working on this codebase.

## Project Overview

This is an **MCP (Model Context Protocol) server** that exposes IncrediBuild build history data to AI assistants. It reads from local SQLite databases and provides query tools via the STDIO transport.

## Technology Stack

- **Language**: Python 3.11+
- **Package Manager**: uv (Astral)
- **Framework**: FastMCP (from `mcp` SDK)
- **Database**: SQLite (read-only)
- **Testing**: pytest + pytest-asyncio
- **Container**: Docker

## Project Structure

```
incredibuild-mcp-server/
├── server.py                 # Main MCP server implementation
├── test_mcp_server.py        # Integration tests (pytest)
├── pyproject.toml            # Project config and dependencies
├── Dockerfile                # Container build
├── readme.md                 # User documentation
├── AGENTS.md                 # This file
└── testdata/
    └── BuildHistoryDB.db     # Sample SQLite database for testing
```

## Key Files

### `server.py`
The main server. Key components:
- `BuildMetadata` - Pydantic model for build data
- `read_builds_in_time_range` - MCP tool to query by absolute timestamps
- `read_recent_builds` - MCP tool to query by relative time
- Uses STDIO transport (spawned by AI clients)

### `test_mcp_server.py`
Integration tests using the MCP Python SDK client. Tests spawn the server as a subprocess and communicate via STDIO.

### `testdata/BuildHistoryDB.db`
Sample SQLite database with 9 build records from a Kodi (XBMC) project. Used for testing.

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `IB_DB_DIR` | Path to directory containing `BuildHistoryDB.db` | Yes |

## Commands

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest -v

# Run specific test
uv run pytest test_mcp_server.py::TestReadBuildsInTimeRange -v

# Build Docker image
docker build -t incredibuild-mcp .

# Test Docker image
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' | \
  docker run -i --rm -v "$(pwd)/testdata:/data" -e IB_DB_DIR=/data incredibuild-mcp
```

## Database Schema

The server reads from `BuildHistoryDB.db` which contains:

```sql
CREATE TABLE build_history (
    BuildId INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    BuildCaption TEXT,              -- User-defined build title
    BuildCommand TEXT,              -- Command executed (e.g., cmake --build ...)
    WorkingDir TEXT,                -- Working directory
    status INTEGER,                 -- 0=running, 1=completed, 3=failed
    BuildTime INTEGER,              -- Duration in milliseconds
    ReturnCode INTEGER,             -- Process exit code
    StartTime INTEGER NOT NULL,     -- Epoch milliseconds
    EndTime INTEGER,                -- Epoch milliseconds
    hasWarnings INTEGER,            -- Boolean flag
    IB_Command TEXT,                -- IncrediBuild command
    Initiator_IP TEXT,              -- IP address of initiator
    UseBuildAvoidCache INTEGER,     -- Cache usage flag
    ApplicationVersion TEXT,        -- IncrediBuild version
    ErrorsNumber INTEGER,           -- Build error count
    WarningsNumber INTEGER,         -- Build warning count
    SysErrorsNumber INTEGER,        -- System error count
    SysWarningsNumber INTEGER,      -- System warning count
    BuildGuid TEXT UNIQUE NOT NULL, -- Unique build identifier
    InitiatorHostName TEXT,         -- Hostname of initiator machine
    BuildTarget TEXT,               -- Build target name
    PredictedExecution INTEGER,     -- Predicted execution time
    LoggingLevel INTEGER,           -- Logging verbosity
    AgentDescription TEXT,          -- Agent info
    LoggedOnUsers TEXT,             -- Users logged on during build
    BuildGroupId TEXT,              -- Build group identifier
    BuildGroupName TEXT,            -- Build group name
    BuildType TEXT,                 -- Type of build
    InitiatorType INTEGER,          -- Type of initiator
    BuildPriority INTEGER,          -- Build priority level
    CoreLimit INTEGER,              -- Core limit for build
    EnvVars TEXT,                   -- JSON: environment variables
    ActiveProjects TEXT,            -- JSON: active projects
    SystemMessages TEXT,            -- JSON: system messages/warnings
    BuildCacheReport TEXT           -- JSON: cache hit/miss details
);
```

## Testing Patterns

Tests use the MCP SDK's `stdio_client` to spawn the server and communicate:

```python
async with stdio_client(get_server_params()) as (read_stream, write_stream):
    async with ClientSession(read_stream, write_stream) as session:
        await session.initialize()
        result = await session.call_tool("read_builds_in_time_range", {...})
```

## Common Tasks

### Adding a new MCP tool
1. Define the tool function in `server.py`
2. Decorate with `@mcp.tool(name="...", description="...")`
3. Add integration tests in `test_mcp_server.py`
4. Run `uv run pytest -v` to verify

### Modifying the database schema
1. Update `BuildMetadata` Pydantic model
2. Update `db_fields` tuple
3. Update tests to verify new fields

### Updating dependencies
1. Edit `pyproject.toml`
2. Run `uv sync`

