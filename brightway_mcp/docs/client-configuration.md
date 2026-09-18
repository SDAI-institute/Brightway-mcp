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
