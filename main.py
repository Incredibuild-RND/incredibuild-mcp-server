"""
IncrediBuild Build History MCP Server

Integration config for Cursor/Claude Desktop (using uv):
{
  "mcpServers": {
    "incredibuild": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/ib-mcp-server", "python", "main.py"],
      "env": {
        "IB_DB_DIR": "/path/to/your/db/folder"
      }
    }
  }
}

For Docker:
{
  "mcpServers": {
    "incredibuild": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-v", "/path/to/db:/data", "-e", "IB_DB_DIR=/data", "incredibuild-mcp"]
    }
  }
}
"""
import os
import sqlite3
from datetime import datetime
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, field_validator

DB_FILE = "BuildHistoryDB.db"
DB_TABLE = "build_history"
SERVER_NAME = "IB-MCP"

build_statuses = ("running", "completed", "stop_forced", "ib_problem_or_user_interrupt", "pending", )

class BuildMetadata(BaseModel):
    BuildCaption: str = Field(
        description="User custom Build title, VS project builds automatically takes the project name as the caption.")
    Status: str = Field(description=f"One of: {', '.join(build_statuses)}.")
    BuildTime: int = Field(description="Representing the total time of the build in milliseconds.")
    StartTime: int = Field(description="Represent the build start time - time from epoch in milliseconds.")
    EndTime: int = Field(description="Represent the build end time - time from epoch in milliseconds.")
    HasWarnings: bool = Field(description="Indicate if the build contains warnings.")
    ErrorsNumber: int = Field(description="Build errors counter.")
    WarningsNumber: int = Field(description="Build warnings counter.")
    SysErrorsNumber: int = Field(description="Build system errors counter.")
    SysWarningsNumber: int = Field(description="Build system warnings counter.")
    EnvVars: str = Field(description="JSON text with list of environment variables.")

    @field_validator("Status", mode="before")
    @staticmethod
    def _norm_status(v):
        if isinstance(v, int):
            try:
                return build_statuses[v]
            except IndexError:
                raise ValueError(f"Invalid status index: {v}")
        if v not in build_statuses:
            raise ValueError(f"Invalid status: {v}")
        return v

    @field_validator("HasWarnings", mode="before")
    @staticmethod
    def _norm_has_warnings(v):
        return bool(v)

    @staticmethod
    def from_tuple(row: tuple) -> "BuildMetadata":
        keys = list(BuildMetadata.model_fields.keys())  # pydantic v2
        return BuildMetadata(**dict(zip(keys, row)))


db_fields = tuple((name, f.annotation.__name__, f.description) for name, f in BuildMetadata.model_fields.items())

def read_db_file(start_timestamp: int, end_timestamp: int, db_path: Path) -> list[tuple]:
    query = (f"SELECT {', '.join(el[0] for el in db_fields)} FROM {DB_TABLE} "
             f"WHERE StartTime >= ? AND StartTime <= ? ORDER BY StartTime")

    with sqlite3.connect(db_path) as con:
        cur = con.cursor()
        db_data = cur.execute(query, (start_timestamp, end_timestamp)).fetchall()
    return db_data

def resolve_db_path(db_dir_str: str) -> Path:
    db_dir = Path(db_dir_str).expanduser().resolve()
    if not db_dir.exists() or not db_dir.is_dir():
        raise SystemExit(f"--db-dir must be an existing directory: {db_dir}")
    db_path = db_dir / DB_FILE
    if not db_path.exists():
        raise SystemExit(f"--db-dir must point to a directory that contains the {DB_FILE} file: {db_dir}")
    return db_path

mcp = FastMCP(SERVER_NAME)

# Validated at startup, used by all tool calls
_db_path: Path | None = None

read_builds_in_time_range_desc = \
    f"""Read which builds were started run between start_timestamp and end_timestamp.
    :param start_timestamp: The earliest build start time to retrieve, from epoch in milliseconds
    :param end_timestamp: The latest build start time to retrieve, from epoch in milliseconds
    :return: A JSON of the build with the following fields: 
    {'\n\t\t'.join(f'{el[0]} ({el[1]}): {el[2]}' for el in db_fields)}
    """

@mcp.tool(name="read_builds_in_time_range", description=read_builds_in_time_range_desc)
def read_builds_in_time_range(start_timestamp: int, end_timestamp: int) -> list[BuildMetadata]:
    return [BuildMetadata.from_tuple(row) for row in read_db_file(start_timestamp, end_timestamp, _db_path)]

read_recent_builds_desc = \
    f"""Read which builds were started run between start_time_ago and end_time_ago.
    :param start_time_ago: The earliest build start time in milliseconds before the tool run time
    :param end_time_ago: The latest build start time in milliseconds before the tool run time
    :return: A JSON of the build with the following fields: 
    {'\n\t\t'.join(f'{el[0]} ({el[1]}): {el[2]}' for el in db_fields)}
    """

@mcp.tool(name="read_recent_builds", description=read_recent_builds_desc)
def read_recent_builds(start_time_ago: int, end_time_ago: int) -> list[BuildMetadata]:
    cur_time = int(datetime.now().timestamp() * 1000)
    return read_builds_in_time_range(cur_time - start_time_ago, cur_time - end_time_ago)

@mcp.resource("config://version")
def get_version():
    return "0.0.1"


def main():
    """Entry point for the MCP server."""
    global _db_path
    
    db_dir = os.environ.get("IB_DB_DIR")
    if not db_dir:
        raise SystemExit(f"Error: Environment variable 'IB_DB_DIR' is not set.\n"
                         f"Set it to the directory containing {DB_FILE}.\n"
                         f"Example: export IB_DB_DIR=/path/to/db/folder")
    
    _db_path = resolve_db_path(db_dir)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
