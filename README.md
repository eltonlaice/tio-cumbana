# Tio *Cumbana*

> An agronomist that watches, remembers, and calls you first.

Built with Opus 4.7 · April 2026
Elton Laice · Maputo, Mozambique

---

## The problem

Smallholder farmers in Lusophone Africa are excluded from agronomy. Extension services don't reach the last mile, private agronomists cost more than a season's profit, and disease, deficiency, or market collapse all show up too late.

## The solution

**Most AI waits for you to ask. Tio Cumbana doesn't.**

A digital agronomist that (1) **watches each parcel** via a long-running agent per farmer, (2) **remembers each farmer** — crops, planting dates, preferences, history — and (3) **speaks in a familiar voice**, in Portuguese with Changana code-switching, via a cloned voice note.

One multimodal Opus 4.7 call: image + audio + context, no separate STT step.

## Stack

- **LLM / vision / audio:** Claude Opus 4.7 (`anthropic` Python SDK)
- **TTS / voice clone:** ElevenLabs
- **Backend:** FastAPI (Python 3.11+, `uv`)
- **Frontend:** Next.js 15, TypeScript, Tailwind, shadcn/ui
- **DB + storage:** Supabase
- **Deploy:** AWS Amplify (frontend) + AWS App Runner (backend), `eu-west-1`

## Run locally

### Backend

```bash
cd backend
uv sync
cp ../.env.example ../.env  # fill in keys
uv run uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000.

## Roadmap (post-hackathon)

- Real WhatsApp Cloud API ingress
- Real long-running Claude Managed Agent loop (per-parcel vigilance)
- Live market-price scrapers (Zimpeto, Mercado Grande)
- NLLB-200 translation fallback for broader language coverage
- Makhuwa, Sena, Ndau support
- SMS / USSD fallback for feature phones
- Drone & satellite integration

## License

MIT. Everything built during the Anthropic "Built with Opus 4.7" hackathon (Apr 21–26, 2026).
