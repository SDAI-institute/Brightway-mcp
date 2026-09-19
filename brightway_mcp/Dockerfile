FROM python:3.11-slim-bookworm

ARG VERSION=0.3.0

LABEL org.opencontainers.image.title="sdai-brightway-mcp" \
      org.opencontainers.image.description="Brightway 2.5 MCP server for SDAI research workflows" \
      org.opencontainers.image.version="${VERSION}"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
