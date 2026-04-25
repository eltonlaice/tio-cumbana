# tio-cumbana-market-prices (MCP server)

A read/write proxy over the Tio Cumbana community price pool. Exposes
three tools for any agent or human operator using Claude Code, Claude
Desktop, or the Managed Agent vigilance loop:

- `get_zimpeto_prices(crop)` — latest + 7-day median for one crop.
- `list_zimpeto_market()` — snapshot across all tracked crops.
- `contribute_price(...)` — append a new observation to the pool.

## Why a community pool, not a scraper?

There is no real-time public API for Zimpeto wholesale prices. SIMA Moç
publishes weekly PDFs, INE aggregates monthly, the rest moves over
WhatsApp. We turned the scarcity into a network effect: the farmers
themselves contribute the prices they see, and the agent serves the
aggregated view back to the next farmer.

## Run

```bash
cd mcp_servers/market_prices
uv sync
TIO_CUMBANA_API_URL=https://wxfvqnx8pe.eu-west-1.awsapprunner.com uv run python server.py
```

For local dev against `localhost:8000`, no env var is needed.

## Wire into Claude Desktop / Claude Code

```json
{
  "mcpServers": {
    "tio-cumbana-market": {
      "command": "uv",
      "args": ["run", "--directory", "/absolute/path/to/mcp_servers/market_prices", "python", "server.py"],
      "env": {
        "TIO_CUMBANA_API_URL": "https://wxfvqnx8pe.eu-west-1.awsapprunner.com"
      }
    }
  }
}
```

## License

MIT.
