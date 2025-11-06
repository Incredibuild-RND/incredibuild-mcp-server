import asyncio
import os
from datetime import datetime as dt

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from mcp.shared.metadata_utils import get_display_name


async def check_session_and_tool_init():
    async with streamablehttp_client("http://localhost:8000/mcp") as (read_stream, write_stream, _, ):
        async with ClientSession(read_stream, write_stream) as session:
            _ = await session.initialize()
            tools = await session.list_tools()
            print(f"Available tools: {[tool.name for tool in tools.tools]}")
            for tool in tools.tools:
                display_name = get_display_name(tool)
                print("----")
                print(f"Tool: {display_name}")
                if tool.description:
                    print(f"{tool.description}")


async def call_tool(tool_name: str, args_dict: dict = None):
    args_dict = args_dict or {}
    async with streamablehttp_client("http://localhost:8000/mcp") as (read_stream, write_stream, _, ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, args_dict)
    return result


if __name__ == "__main__":
    asyncio.run(check_session_and_tool_init())
    args_dict = {"start_timestamp": 0, "end_timestamp": int(dt.now().timestamp() * 1000)}
    request_result = asyncio.run(call_tool("read_builds_in_time_range", args_dict)).content
    print("read_builds_in_time_range result on all time:")
    for el in request_result:
        print(el)
    print("---")
    args_dict = {"start_time_ago": int(dt.now().timestamp() * 1000), "end_time_ago": 0}
    request_result = asyncio.run(call_tool("read_recent_builds", args_dict)).content
    print("read_recent_builds result on all time:")
    for el in request_result:
        print(el)
    print("Done!")
