"""Integration tests for the IncrediBuild MCP Server."""
import json
import os
import sys
from pathlib import Path

from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

SERVER = Path(__file__).parent / "server.py"
TESTDATA = Path(__file__).parent / "testdata"

PARAMS = StdioServerParameters(
    command=sys.executable,
    args=[str(SERVER)],
    env={**os.environ, "IB_DB_DIR": str(TESTDATA)},
)


def mcp_test(fn):
    """Decorator that provides an initialized MCP session to the test."""
    async def test():
        async with stdio_client(PARAMS) as (r, w):
            async with ClientSession(r, w) as s:
                await s.initialize()
                await fn(s)
    test.__name__ = fn.__name__
    return test


@mcp_test
async def test_lists_tools(s):
    tools = await s.list_tools()
    assert [t.name for t in tools.tools] == ["read_builds_in_time_range", "read_recent_builds"]


@mcp_test
async def test_returns_9_builds(s):
    result = await s.call_tool("read_builds_in_time_range", {"start_timestamp": 0, "end_timestamp": 10**13})
    assert len(result.content) == 9


@mcp_test
async def test_filters_by_timestamp(s):
    result = await s.call_tool("read_builds_in_time_range", {"start_timestamp": 1764777170000, "end_timestamp": 1764777170200})
    assert len(result.content) == 1


@mcp_test
async def test_status_is_string(s):
    result = await s.call_tool("read_builds_in_time_range", {"start_timestamp": 0, "end_timestamp": 10**13})
    build = json.loads(result.content[0].text)
    assert build["Status"] in {"running", "completed", "stop_forced", "ib_problem_or_user_interrupt", "pending"}


@mcp_test
async def test_recent_builds(s):
    result = await s.call_tool("read_recent_builds", {"start_time_ago": 10**15, "end_time_ago": 0})
    assert len(result.content) == 9


@mcp_test
async def test_version_resource(s):
    result = await s.read_resource("config://version")
    assert result.contents[0].text == "0.0.1"
