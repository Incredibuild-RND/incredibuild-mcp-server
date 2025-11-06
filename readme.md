# MCP Build History Server

A minimal [Model Context Protocol](https://modelcontextprotocol.io) (MCP) server that 
exposes build history from local SQLite files.
The server provides a 2 tools, `read_builds_in_time_range` and `read_recent_builds`, 
for querying builds between two timestamps.

---
## Features
* ✅ Simple MCP server using `FastMCP`
* ✅ Pluggable data location via `IbDbDir` env var (no hardcoded paths)
* ✅ Returns JSON list of builds

---
## Requirements
* Python 3.13+
* SQLite databases available on your initiator machines

---
## Installation
Windows:
```CMD
uv venv ib_mcp --python 3.13
ib_mcp\Scripts\activate
uv pip install fastmcp pydantic
setx IbDbDir "<your-db-dir-here>"
cd <repo-dir>
git clone https://github.com/scientistl/ib-mcp-server.git
python 
```
Bash:
```bash
uv venv ib_mcp --python 3.13
source ib_mcp/bin/activate
uv pip install fastmcp pydantic
echo 'export IbDbDir=<your-db-dir-here>' >> ~/.bashrc
source ~/.bashrc
cd <repo-dir>
git clone https://github.com/scientistl/ib-mcp-server.git
```

---
## Quick Start
```
cd <your-repo>
python build_history_mcp.py
```

---
## Check the installation
Reads the tool description and reads all the lines in the file.
```
cd <your-repo>
python build_history_mcp_check.py
```
## MCP Interface
### Tool: `read_builds_in_time_range`
Read which builds started between `start_timestamp` and `end_timestamp`.

**Parameters**
* `start_timestamp` (int): earliest build start (epoch milliseconds)
* `end_timestamp` (int): latest build start (epoch milliseconds)

**Returns**
* `list[BuildMetadata]` serialized to JSON.


### Tool: `read_recent_builds`
Read which builds started between `start_timestamp` and `end_timestamp`.

**Parameters**
* `started_milisec_ago` (int): earliest build start time in miliseconds before the tool run time
* `end_milisec_ago` (int): latest build start time in miliseconds before the tool run time

**Returns**
* `list[BuildMetadata]` serialized to JSON.

## Security Notes

* The server reads local SQLite files only. If you serve it remotely, ensure the process user has least-privilege access to the DB directory.
