# Development notes — Tio Cumbana

This project was built end-to-end with **Claude Code** during the *Built with Opus 4.7: a Claude Code hackathon* (Cerebral Valley × Anthropic, Apr 21–28, 2026), in a 29-hour active-work window split between Friday night, Saturday in Maluana, and Sunday in Maputo.

The commit log is the development trajectory. Every commit is co-authored by Claude Opus 4.7; the README and the system prompt persona were iterated jointly between the human builder and Claude.

## Anthropic platform — what we use and where

| Capability | Where it lives | What it does here |
|---|---|---|
| **Claude Opus 4.7 via Messages API** | [`backend/app/services/anthropic_client.py`](backend/app/services/anthropic_client.py) | The reasoning core. One multimodal call per consult: image (plant photo) + text (transcript + farmer Memory). |
| **Claude Code (CLI)** | This repo's commit log | Every line of code, every commit, every refactor — written through Claude Code. |
| **Sub-agents** (Explore, Plan, code-reviewer) | Used at session-time | Explore mapped the Anthropic docs to confirm Messages API does **not** accept audio content blocks today (Apr 2026), forcing the STT bridge. Plan agent shaped the Managed Agents stub. |
| **Claude Managed Agents** | [`backend/app/services/managed_agent.py`](backend/app/services/managed_agent.py) | The autonomous per-parcel vigilance loop. Uses `client.beta.agents.create` + `beta.environments.create` + `beta.sessions.events.stream` with the `managed-agents-2026-04-01` beta header. Feature-flagged for the demo. |
| **Agent SDK toolset** | Same module | The Managed Agent is provisioned with `agent_toolset_20260401`, giving it the full pre-built tool set (bash, file, web). |
| **MCP servers** | [`mcp_servers/weather/`](mcp_servers/weather/) | A FastMCP server exposing `get_weather(latitude, longitude)` to the vigilance agent. Backed by Open-Meteo (no API key) with a built-in mildew-risk heuristic. |
| **Agent Skills** | [`skills/diagnose-mildew/`](skills/diagnose-mildew/) | A reusable diagnostic skill with `SKILL.md` + treatment reference. Memory-aware (respects per-farmer product preferences). |

## Sub-agents used during this build

These are notes for anyone reading the repo who wants to see how Claude Code's sub-agent palette was actually used in practice — not just listed.

- **`Explore`** — mapped Anthropic's vision/multimodal docs to verify the audio-input content-block format. The result: as of Apr 2026 the Messages API does not accept audio. That single finding redirected the architecture from "one call image+audio+text" to "STT bridge → image+text", documented honestly in the README.
- **`Explore`** — surveyed open-source TTS options (XTTS-v2, F5-TTS, OpenVoice, Piper) to evaluate a fallback for ElevenLabs. Findings: only OpenVoice has a usable OSS license, but no native Portuguese model. Logged as a v2 path.
- **`Plan`** — sketched the Managed Agents vigilance loop interface before code was written.

## What deliberately did NOT make it in

The hackathon brief (`CLAUDE.md` §9) lists explicit out-of-scope items. Sticking to it is the discipline that keeps a 29-hour build coherent. Notable choices:

- **No second LLM/STT vendor.** Brief §8 pins Anthropic + ElevenLabs only. We did not introduce OpenAI Whisper, Google Cloud, or any other proprietary model — even though Whisper would have been a quick Plan B for STT. The single non-Anthropic dependency is ElevenLabs, justified by Anthropic not offering voice cloning, and disclosed in the README.
- **No real WhatsApp Cloud API integration.** Approval cycle is too long; web demo mimics the WhatsApp chat feel.
- **No real long-running Managed Agent in the demo.** The loop is provisioned and ready (`services/managed_agent.py` is real Anthropic SDK code, not a stub note); the demo trigger is scripted via `/api/proactive` for budget and reproducibility.
- **No Whisper fallback path** in the deployed pipeline — even though it was scoped in the brief as a Plan B. The interface was designed to make it a drop-in (STT/TTS Protocols), but adding it now would require introducing OpenAI as a vendor without justification.
- **No tests beyond a small smoke set.** Honest call: time goes to voice corpus and the 3-minute video, not to coverage. Documented as roadmap.

## CI/CD

- **Frontend (Amplify):** webhook from GitHub `main` → Amplify rebuilds → Next.js `output: 'export'` → static site at `*.amplifyapp.com`. (Static export chosen over Amplify Compute to dodge a Next.js 16 / Amplify adapter incompatibility — documented in the commit message of `3cd0134`.)
- **Backend (App Runner):** GitHub Actions OIDC role assumes into AWS, builds `linux/amd64`, pushes to ECR. App Runner has `AutoDeploymentsEnabled` and picks up the new `:latest` tag without further action.
- **Secrets:** SSM Parameter Store SecureString. Injected as App Runner `RuntimeEnvironmentSecrets`. No API key has ever been committed; `.env` is git-ignored.

## Running locally

See the [README](README.md) for the canonical local-run instructions. Short version: `uv sync && uv run uvicorn app.main:app --reload` for the backend, `npm install && npm run dev` for the frontend.
