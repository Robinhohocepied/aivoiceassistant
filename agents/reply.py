import logging
from typing import Optional, List, Tuple

from app.config import Settings
from agents.client import create_agents_client

logger = logging.getLogger(__name__)


DEFAULT_PROMPT_FR = (
    "Vous êtes un assistant de prise de rendez-vous pour une clinique. "
    "Répondez en français, de façon concise et polie. "
    "Objectif: recueillir 1) nom complet, 2) email, 3) date/heure souhaitée, 4) motif. "
    "Comportement:\n"
    "- Au premier message: répondez librement (accueil naturel), puis demandez les informations manquantes.\n"
    "- À chaque tour: n'insistez que sur les informations manquantes.\n"
    "- Proposez 2-3 créneaux parmi 'Créneaux disponibles prochains' si cela aide.\n"
    "- Ne confirmez jamais un rendez-vous ni une disponibilité exacte : ce sont des propositions à vérifier.\n"
)


Message = Tuple[str, str]  # (role, content)


async def generate_reply(
    user_text: str,
    settings: Settings,
    history: Optional[List[Message]] = None,
    availability_slots: Optional[List[str]] = None,
) -> str:
    """Return a reply text using OpenAI if configured, otherwise a safe fallback.

    - Uses `settings.agent_prompt` or a default French intake prompt.
    - Uses `settings.agent_model` (default gpt-4.1).
    - Falls back to a fixed message if OpenAI is not configured or errors.
    """
    system_prompt = settings.agent_prompt or DEFAULT_PROMPT_FR

    client = create_agents_client(settings)
    if client is None:
        logger.info("openai client not configured; using fallback reply")
        return (
            "Merci. Pouvez-vous me donner votre nom complet, s’il vous plaît ?"
        )

    try:
        # Build message list with optional recent conversation and availability hints
        messages: List[dict] = [
            {"role": "system", "content": system_prompt},
        ]
        if availability_slots:
            readable = "\n".join(f"- {s}" for s in availability_slots)
            messages.append({
                "role": "system",
                "content": f"Créneaux disponibles prochains (heure locale):\n{readable}",
            })
        if history:
            for role, content in history[-6:]:
                messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": user_text})

        # Use Chat Completions for simplicity and stability.
        resp = client.chat.completions.create(
            model=settings.agent_model,
            messages=messages,
            temperature=0.3,
            max_tokens=300,
        )
        content: Optional[str] = None
        if resp.choices and resp.choices[0].message and resp.choices[0].message.content:
            content = resp.choices[0].message.content
        if content:
            return content.strip()
        logger.warning("openai returned empty content; using fallback reply")
    except Exception as exc:  # noqa: BLE001
        logger.exception("openai generation failed: %s", exc)

    return "Merci. Pouvez-vous me donner votre nom complet, s’il vous plaît ?"
