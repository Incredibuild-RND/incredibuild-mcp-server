# IncrediBuild MCP Server

A [Model Context Protocol](https://modelcontextprotocol.io) (MCP) server that lets AI assistants query your IncrediBuild build history.

## Features

* ✅ `stdio` transport for seamless AI client integration
* ✅ Two query tools: by absolute timestamps or relative time
* ✅ Docker support for containerized deployment
* ✅ Configurable database location via environment variable

---

## Quick Start

```bash
docker run -i --rm \
  -v /path/to/your/db/folder:/data \
  ghcr.io/incredibuild-rnd/incredibuild-mcp-server:v0.1.0
```

---

## Integration with AI Clients

### Cursor / Claude Desktop

Add to your MCP configuration (`~/.cursor/mcp.json` or Claude Desktop settings):

```json
{
  "mcpServers": {
    "incredibuild": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-v", "/path/to/your/db/folder:/data",
        "ghcr.io/incredibuild-rnd/incredibuild-mcp-server:v0.1.0"
      ]
    }
  }
}
```

Replace `/path/to/your/db/folder` with the directory containing your `BuildHistoryDB.db`.

**Windows example** (path is typically `C:\ProgramData\Incredibuild\Manager\`):

```json
{
  "mcpServers": {
    "incredibuild": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-v", "C:/ProgramData/Incredibuild/Manager:/data",
        "ghcr.io/incredibuild-rnd/incredibuild-mcp-server:v0.1.0"
      ]
    }
  }
}
```

---

## MCP Tools

### `read_builds_in_time_range`

Query builds that started between two absolute timestamps.

| Parameter | Type | Description |
|-----------|------|-------------|
| `start_timestamp` | int | Earliest build start (epoch milliseconds) |
| `end_timestamp` | int | Latest build start (epoch milliseconds) |

### `read_recent_builds`

Query builds relative to the current time.

| Parameter | Type | Description |
|-----------|------|-------------|
| `start_time_ago` | int | Earliest build (ms before now) |
| `end_time_ago` | int | Latest build (ms before now) |

**Returns**: List of `BuildMetadata` objects with:
- `BuildCaption`, `Status`, `BuildTime`, `StartTime`, `EndTime`
- `HasWarnings`, `ErrorsNumber`, `WarningsNumber`
- `SysErrorsNumber`, `SysWarningsNumber`, `EnvVars`

---

## Development

```bash
# Clone
git clone https://github.com/Incredibuild-RND/incredibuild-mcp-server.git
cd incredibuild-mcp-server

# Install
uv sync

# Test
uv run pytest -v

# Run locally
IB_DB_DIR=./testdata uv run python main.py
```

---

## License

See [License](LICENSE)
