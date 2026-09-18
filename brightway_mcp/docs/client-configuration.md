# Brightway MCP Client Configuration

Use stdio for local developer clients and streamable HTTP only when a client needs an HTTP MCP endpoint.

## Local stdio

Install the MCP package in the Python environment that contains Brightway:

```bash
cd Brightway2/brightway_mcp
pip install -e .
```

Example MCP client configuration:

```json
{
  "mcpServers": {
    "brightway": {
      "command": "python",
      "args": ["-m", "brightway_mcp.server"],
      "env": {
        "BRIGHTWAY_READ_ONLY": "true"
      }
    }
  }
}
```

Use the absolute Python executable from the Brightway environment when the client does not inherit the intended environment.

## Local HTTP

Start the server:

```bash
python -m brightway_mcp.server --http
```

The server binds to the local host on port 8000 by default. Keep it local unless an authenticated gateway or secure tunnel is intentionally configured.

## First client calls

Use this sequence before running a study:

```text
health_check
→ list_projects
→ list_databases(project=...)
→ list_methods(project=...)
```

Stop and resolve project/database/method ambiguity before calculating.

## Read-only mode

Set:

```text
BRIGHTWAY_READ_ONLY=true
```

for inspection, benchmarking, or public demonstrations. This blocks project/database writes, uncertainty mutation, LCIA-method import, and result-file export while retaining read/calculation operations.

## Remote clients

For any remote, web-hosted, or sandboxed MCP client, front the HTTP server with an authenticated HTTPS gateway, VPN, or secure tunnel appropriate to that client. Do not expose a raw Brightway runtime to the public internet.

After changing tool schemas, reload/rescan tools in the client and run a small non-destructive verification call.