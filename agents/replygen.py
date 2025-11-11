from __future__ import annotations

from typing import List, Optional

from app.config import Settings
from agents.client import create_agents_client
from agents.datetime_fr import format_fr_human


STYLE_GUIDE = (
    "Tu es l’assistant du cabinet (dentaire)."
    " Utilise le vouvoiement, un ton empathique, clair et professionnel."
    " Réponds en FRANÇAIS en UNE SEULE PHRASE (une ligne), ≤ 220 caractères,"
    " sans salutations inutiles, sans liste, sans plusieurs questions."
)


def _sanitize_oneline(text: str, max_len: int = 220) -> str:
    t = (text or "").replace("\n", " ").replace("\r", " ").strip()
    # collapse multiple spaces
    while "  " in t:
        t = t.replace("  ", " ")
    if len(t) > max_len:
        t = t[: max_len - 1].rstrip() + "…"
    return t


def _call_openai(settings: Settings, system: str, user: str) -> Optional[str]:
    client = create_agents_client(settings)
    if client is None:
        return None
    try:
        resp = client.responses.create(
            model=settings.agent_model,
            input=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=0.3,
            max_output_tokens=220,
        )
        text = getattr(resp, "output_text", None) or str(resp)
        return text.strip()
    except Exception:
        return None


def followup_missing(
    settings: Settings,
    *,
    ask_field: str,
    name: Optional[str],
    reason: Optional[str],
    preferred_time: Optional[str],
    already_asked: Optional[List[str]] = None,
) -> Optional[str]:
    system = STYLE_GUIDE
    asked = ", ".join(already_asked or []) or "aucun"
    field_label = {
        "name": "votre nom complet",
        "reason": "la raison de votre visite",
        "preferred_time": "votre préférence de date/heure",
    }.get(ask_field, ask_field)
    user = (
        "Contexte (peut contenir des valeurs manquantes):\n"
        f"- Nom: {name or '—'}\n"
        f"- Raison: {reason or '—'}\n"
        f"- Préférence: {preferred_time or '—'}\n"
        f"Champs déjà demandés (ne pas répéter): {asked}\n\n"
        "Objectif: Demander UNIQUEMENT le champ ciblé, de façon polie et concise."
        " Une seule phrase (une ligne), ≤ 220 caractères."
        f" Champ ciblé: {field_label}."
        " Ne pas répéter un champ déjà demandé. Ne pas ajouter d'autres questions."
        " Répondre uniquement avec le texte du message."
    )
    out = _call_openai(settings, system, user)
    return _sanitize_oneline(out or "") if out else None


def confirmation(settings: Settings, *, name: Optional[str], reason: Optional[str], preferred_time_iso: str) -> Optional[str]:
    system = STYLE_GUIDE
    date_h = format_fr_human(preferred_time_iso)
    user = (
        f"Variables:\n- date_long: {date_h}\n- nom: {name or '—'}\n- raison: {reason or '—'}\n\n"
        "Rédige une confirmation de réservation en une phrase claire."
        " Inclure l’idée: ‘Vous recevrez un rappel 24h avant’."
        " Ne renvoyez que le texte du message."
    )
    return _call_openai(settings, system, user)


def alternatives(settings: Settings, *, options_iso: List[str]) -> Optional[str]:
    system = STYLE_GUIDE
    items = [f"{i+1}) {format_fr_human(iso)}" for i, iso in enumerate(options_iso)]
    listing = "\n".join(items)
    user = (
        "Présenter des créneaux disponibles au patient, sous forme de liste numérotée.\n"
        "Préfixe suggéré: ‘Voici des créneaux disponibles :’.\n"
        f"Liste:\n{listing}\n\n"
        "Terminer par: ‘Répondez 1 ou 2 pour choisir.’\n"
        "Ne renvoyez que le texte du message."
    )
    return _call_openai(settings, system, user)
