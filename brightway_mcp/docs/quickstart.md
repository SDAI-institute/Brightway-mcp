# Brightway MCP Quick Start

Use the Brightway MCP server to inspect or build a Brightway 2.5 project, run LCIA, interpret stored results, and dispose result state through typed MCP tools.

## Requirements

- Python 3.11+
- Brightway 2.5-compatible packages (`bw2data>=4`, `bw2calc>=2`, `bw2io>=0.9`)
- the `brightway-mcp` package/repository
- an existing Brightway project, or permission to bootstrap one

The reviewed package version is 0.1.0.

## 1. Install

```bash
cd Brightway2/brightway_mcp
pip install -e .
```

For development and tests:

```bash
pip install -e ".[dev]"
```

## 2. Start the server

Local stdio:

```bash
python -m brightway_mcp.server
```

Streamable HTTP on the local host:

```bash
python -m brightway_mcp.server --http
```

The installed console script is also available as:

```bash
brightway-mcp
```

