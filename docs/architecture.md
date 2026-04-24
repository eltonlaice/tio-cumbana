# Architecture

```
┌────────────────────────────────────────────────────────┐
│  Farmer — Web UI (Next.js, WhatsApp-inspired)          │
│  photo + voice note + phone number                     │
└────────────────────────┬───────────────────────────────┘
                         ▼
┌────────────────────────────────────────────────────────┐
│  Orchestrator — FastAPI                                │
│  • Load farmer Memory + parcel context from Supabase   │
│  • Compose single multimodal request                   │
└────────────────────────┬───────────────────────────────┘
                         ▼
┌────────────────────────────────────────────────────────┐
│  Opus 4.7 — ONE multimodal call                        │
│  content blocks: image + audio + text (+ memory)       │
│  system: Tio Cumbana persona (PT + Changana)           │
└────────────────────────┬───────────────────────────────┘
                         ▼
┌────────────────────────────────────────────────────────┐
│  ElevenLabs — TTS with cloned voice                    │
└────────────────────────┬───────────────────────────────┘
                         ▼
                 Farmer receives voice note

     ┌────────────────────────────────┐
     │  Proactive trigger (scripted)  │
     │  Button / cron → same pipeline │
     │  but farmer did not ask        │
     └────────────────────────────────┘
```

## Key decision: one multimodal call

Audio is passed directly to Opus 4.7 alongside the photo and the farmer context. No separate STT. Reasons: hackathon is Opus-focused, better handling of PT/Changana code-switching, lower latency, stronger narrative.

## Deploy

- **Frontend:** AWS Amplify (Next.js), `*.amplifyapp.com`
- **Backend:** AWS App Runner (container), `*.awsapprunner.com`
- **Region:** `eu-west-1` (Ireland)
- **Secrets:** SSM Parameter Store (SecureString) or App Runner env vars
