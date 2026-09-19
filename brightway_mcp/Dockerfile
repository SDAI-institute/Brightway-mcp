FROM python:3.11-slim-bookworm

ARG VERSION=0.3.0

LABEL org.opencontainers.image.title="sdai-brightway-mcp" \
      org.opencontainers.image.description="Brightway 2.5 MCP server for SDAI research workflows" \
      org.opencontainers.image.version="${VERSION}"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY src/ ./src/
RUN pip install --no-cache-dir .

RUN useradd -m -u 1000 mcp \
    && mkdir -p /data/brightway \
    && chown -R mcp:mcp /app /home/mcp /data/brightway
USER mcp

ENV HOME=/home/mcp \
    PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["python", "-m", "brightway_mcp.server", "--http"]
