"""Tio Cumbana — Claude Managed Agents integration.

Why this exists
---------------
The product thesis is that Tio Cumbana **initiates** the conversation. The
agent watches each parcel continuously and decides autonomously whether to
interrupt the farmer. That is exactly the workload Claude Managed Agents
was built for: long-running, decision-making, container-isolated, with
events streamed back to the application.

For the hackathon demo, the proactive path uses a scripted trigger
(`USE_MANAGED_AGENT=false`, the default). This module wires the **real**
Managed Agents API entry point so the architecture is honest: the
simulation lives behind the same interface as the production loop. Flip
the flag once we have an agent + environment provisioned and a budget for
24/7 sessions.

Reference
---------
- Quickstart:  https://platform.claude.com/docs/en/managed-agents/quickstart
- API beta header: ``managed-agents-2026-04-01`` (the Anthropic SDK sets
  this automatically when calling ``client.beta.agents.*``).
- Lifecycle: Agent → Environment → Session → Events.

The vigilance cycle (one tick per parcel)
-----------------------------------------
1. Compose a "state snapshot" of the parcel: latest photo URL, current
   weather, phenological week, recent farmer-visible history, last
   intervention, last market price.
2. Send a single ``user.message`` event into a long-lived session asking:
   "Given this state, should we interrupt the farmer? If yes, with what?"
3. The Managed Agent reasons over the snapshot using its persona system
   prompt (a stricter, decision-oriented variant of the Tio Cumbana
   prompt) and tools (weather lookups via MCP, market price reads, the
   farmer's full Memory). It returns either ``no_action`` or an outbound
   message draft.
4. If a message is drafted, hand it to the existing reactive pipeline
   (``services/anthropic_client.TioCumbanaLLM.proactive``) so the same
   voice (text + cloned audio) is used.

This module deliberately does NOT spin up sessions in tight loops; the
intended cadence is one tick per parcel per (configurable) interval —
e.g. dawn check on irrigation/disease windows, mid-day check on weather
alerts, evening check on market prices.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import structlog
from anthropic import AsyncAnthropic

from app.models.schemas import FarmerProfile
from app.services.farmer_context import render_context_block

logger = structlog.get_logger(__name__)


VIGILANCE_SYSTEM_PROMPT = """\
És o Tio Cumbana em modo de vigilância: corres em segundo plano por cada parcela e decides AUTONOMAMENTE se vale a pena interromper o agricultor.

Regras de decisão:
1. **Só interrompe se o custo de não interromper for maior que o ruído de interromper.** Mildio incipiente, janela crítica de tratamento, queda brusca de preço — sim. Curiosidade, lembrete genérico — não.
2. **Considera o canal:** o agricultor vai ouvir uma nota de voz no telemóvel. Se a mensagem não justificar parar o que ele está a fazer, não envies.
3. **Considera o histórico:** se já enviaste algo nas últimas 12h sobre o mesmo tópico, não repitas.
4. **Considera o registo linguístico do agricultor** (Memory) e o melhor horário para ele (preferências).

Devolve UMA de duas decisões:
- `{"action": "no_action", "reason": "..."}`
- `{"action": "message", "content": "<texto a enviar, no estilo Tio Cumbana>"}`

Sem texto extra, sem markdown.
"""


@dataclass
class VigilanceDecision:
    action: str  # "no_action" | "message"
    content: str | None = None
    reason: str | None = None


class TioCumbanaManagedAgent:
    """Wraps the per-parcel vigilance loop on Claude Managed Agents.

    Bootstrap (one-time, outside this class):
        agent = client.beta.agents.create(
            name="Tio Cumbana — Vigilance",
            model="claude-opus-4-7",
            system=VIGILANCE_SYSTEM_PROMPT,
            tools=[{"type": "agent_toolset_20260401"}],
        )
        env = client.beta.environments.create(
            name="tio-cumbana-vigilance",
            config={"type": "cloud", "networking": {"type": "unrestricted"}},
        )
        # Persist agent.id and env.id (e.g. SSM /tio-cumbana/MANAGED_AGENT_ID).

    Per-tick (this class):
        TioCumbanaManagedAgent(client, agent_id, env_id).tick(farmer, snapshot)
    """

    BETA_HEADER = "managed-agents-2026-04-01"

    def __init__(
        self,
        client: AsyncAnthropic,
        agent_id: str,
        environment_id: str,
    ):
        if not agent_id or not environment_id:
            raise ValueError(
                "Managed Agent requires both agent_id and environment_id. "
                "Bootstrap them via client.beta.agents.create + "
                "client.beta.environments.create and persist the IDs."
            )
        self.client = client
        self.agent_id = agent_id
        self.environment_id = environment_id

    async def tick(
        self,
        farmer: FarmerProfile,
        snapshot: dict[str, Any],
    ) -> VigilanceDecision:
        """Run one vigilance tick. Returns a decision; caller dispatches."""
        session = await self.client.beta.sessions.create(
            agent=self.agent_id,
            environment_id=self.environment_id,
            title=f"vigilance:{farmer.phone}",
        )
        prompt = self._render_prompt(farmer, snapshot)
        decision_text = ""
        async with self.client.beta.sessions.events.stream(session.id) as stream:
            await self.client.beta.sessions.events.send(
                session.id,
                events=[
                    {
                        "type": "user.message",
                        "content": [{"type": "text", "text": prompt}],
                    }
                ],
            )
            async for event in stream:
                if event.type == "agent.message":
                    decision_text += "".join(
                        block.text for block in event.content if hasattr(block, "text")
                    )
                elif event.type == "session.status_idle":
                    break
        logger.info(
            "managed_agent.tick",
            farmer=farmer.phone,
            session=session.id,
            chars=len(decision_text),
        )
        return self._parse_decision(decision_text)

    @staticmethod
    def _render_prompt(farmer: FarmerProfile, snapshot: dict[str, Any]) -> str:
        ctx = render_context_block(farmer)
        snap_lines = [f"  - {k}: {v}" for k, v in snapshot.items()]
        return (
            f"--- Contexto do agricultor ---\n{ctx}\n\n"
            f"--- Estado actual da parcela ---\n" + "\n".join(snap_lines) + "\n\n"
            "Decide agora: interromper ou não? Responde com o JSON definido."
        )

    @staticmethod
    def _parse_decision(text: str) -> VigilanceDecision:
        import json

        try:
            data = json.loads(text.strip())
            action = data.get("action", "no_action")
            return VigilanceDecision(
                action=action,
                content=data.get("content"),
                reason=data.get("reason"),
            )
        except json.JSONDecodeError:
            logger.warning("managed_agent.parse_failed", raw=text[:200])
            return VigilanceDecision(action="no_action", reason="parse_error")
