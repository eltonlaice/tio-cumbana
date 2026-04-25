# Tio *Cumbana*

> An agronomist that watches, remembers, and calls you first.

[![Built with Claude Code](https://img.shields.io/badge/Built%20with-Claude%20Code-1A1410?labelColor=F5EDD9)](https://claude.com/product/claude-code)
[![Powered by Opus 4.7](https://img.shields.io/badge/Powered%20by-Claude%20Opus%204.7-9F3E26?labelColor=F5EDD9)](https://claude.com/)
[![CI](https://github.com/eltonlaice/tio-cumbana/actions/workflows/ci.yml/badge.svg)](https://github.com/eltonlaice/tio-cumbana/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-3D5A3A?labelColor=F5EDD9)](LICENSE)

Built for *Built with Opus 4.7: a Claude Code hackathon* · April 2026
Elton Laice · Maputo, Mozambique

**Live:** [main.d3die8p0fcsnpg.amplifyapp.com](https://main.d3die8p0fcsnpg.amplifyapp.com/) · **API:** [wxfvqnx8pe.eu-west-1.awsapprunner.com](https://wxfvqnx8pe.eu-west-1.awsapprunner.com/health)

---

## The problem

Smallholder farmers — **500 million globally, sustaining 2.5 billion people and producing roughly a third of the world's food** — are largely excluded from agronomy by language, literacy, and the cost of expertise. In Mozambique alone, **3.2 million households** face this gap; across Sub-Saharan Africa, ~33 million.

Extension services don't reach the last mile, private agronomists cost more than a season's profit, and disease, deficiency, or market collapse all show up too late.

I run a 54-row commercial farm in Maluana with my mother — cucumber, bell pepper, seed potato — sandy soil that drinks water in minutes. The nearest agronomist is 40 km away. This is not a hypothetical; it is the use case.

## The solution

**Most AI waits for you to ask. Tio Cumbana doesn't.**

A digital agronomist that:

1. **Watches each parcel** — a long-running Managed Agent (per farmer) cross-references photos, weather, and market prices, and decides autonomously whether to interrupt.
2. **Remembers each farmer** — crops, planting dates, preferences, history. Two farmers asking the same question receive two different answers because they are two different people.
3. **Speaks in a familiar voice** — Portuguese with Changana code-switching, delivered as a voice note in the builder's cloned voice. In Maluana, people already call me Tio Cumbana.

## Anthropic platform — what's wired and where

A single coherent stack of Claude Code / Claude API capabilities; not a checklist.

| Capability | Where in the repo |
|---|---|
| Claude Opus 4.7 (Messages API, multimodal) | [`backend/app/services/anthropic_client.py`](backend/app/services/anthropic_client.py) |
| Claude Code (CLI) — used for the entire build | Commit log (every commit is co-authored by Claude Opus 4.7) |
| Sub-agents (Explore, Plan) — used during build | See [`DEVELOPMENT.md`](DEVELOPMENT.md) |
| Claude Managed Agents (vigilance loop) | [`backend/app/services/managed_agent.py`](backend/app/services/managed_agent.py) |
| Agent SDK toolset (`agent_toolset_20260401`) | Same module |
| MCP server (weather feed for the agent) | [`mcp_servers/weather/`](mcp_servers/weather/) |
| Agent Skill (reusable diagnostic skill) | [`skills/diagnose-mildew/`](skills/diagnose-mildew/) |

Architecture, design choices, and what was deliberately scoped out: see [`DEVELOPMENT.md`](DEVELOPMENT.md) and [`docs/architecture.md`](docs/architecture.md).

## Stack

- **LLM / vision:** Claude Opus 4.7 (`anthropic` Python SDK)
- **STT:** ElevenLabs Scribe (Anthropic Messages API does not yet accept audio content blocks; documented in `services/stt.py`)
- **TTS / voice clone:** ElevenLabs (only non-Anthropic vendor; Anthropic does not offer voice cloning)
- **Backend:** FastAPI (Python 3.11+, `uv`) on AWS App Runner
- **Frontend:** Next.js 16, TypeScript, Tailwind v4 — static export on AWS Amplify
- **Secrets:** SSM Parameter Store (SecureString), injected as App Runner `RuntimeEnvironmentSecrets`
- **CI/CD:** GitHub Actions (OIDC) → ECR → App Runner; GitHub → Amplify

## Run locally

```bash
# Backend
cd backend
uv sync
cp ../.env.example ../.env  # fill in ANTHROPIC_API_KEY, ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID
uv run uvicorn app.main:app --reload --port 8000

# Frontend (in a separate shell)
cd frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Roadmap (post-hackathon)

- Real WhatsApp Cloud API ingress
- Real long-running Claude Managed Agent loop running 24/7 per parcel
- Live market-price scrapers (Zimpeto, Mercado Grande)
- NLLB-200 translation fallback for broader language coverage
- Makhuwa, Sena, Ndau support
- SMS / USSD fallback for feature phones
- Drone & satellite integration
- A Portuguese-native open-source voice model trained from the captured Mozambican corpus, removing the ElevenLabs dependency

## License

MIT. Everything in this repo was built during the Anthropic *Built with Opus 4.7* hackathon (Apr 21–28, 2026).
