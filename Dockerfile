# syntax=docker/dockerfile:1
FROM python:3.13-slim

WORKDIR /app

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files
COPY pyproject.toml .
COPY main.py .

# Install dependencies using uv
RUN uv pip install --system --no-cache .

ENV IB_DB_DIR=/data

# Run the MCP server in STDIO mode
ENTRYPOINT ["python", "main.py"]

