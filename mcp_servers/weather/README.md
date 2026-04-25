# tio-cumbana-weather (MCP server)

A minimal MCP server consumed by Tio Cumbana's autonomous vigilance loop.
Exposes one tool — `get_weather(latitude, longitude)` — backed by the free
Open-Meteo API. Includes a mildew-risk heuristic tuned for cucumber downy
mildew in Mozambican coastal climates.

## Run

```bash
cd mcp_servers/weather
uv sync
uv run python server.py
```

## Wire into Claude Desktop / Claude Code

Add to `~/.claude/mcp.json` (or the equivalent for your client):

```json
{
  "mcpServers": {
    "tio-cumbana-weather": {
      "command": "uv",
      "args": ["run", "--directory", "/absolute/path/to/mcp_servers/weather", "python", "server.py"]
    }
  }
}
```

## Wire into a Managed Agent

When provisioning the vigilance Agent (see `backend/app/services/managed_agent.py`),
register this server in the agent's `mcp_servers` list. The autonomous loop will
then call `get_weather` whenever it needs to decide if conditions warrant
interrupting a farmer.

## License

MIT.
