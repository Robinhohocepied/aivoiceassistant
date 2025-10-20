import json
from typing import Dict, List, Optional, Tuple

from agents.session import SessionState


FIELDS = ("name", "reason", "preferred_time")


def build_extraction_prompt(text: str, state: SessionState) -> str:
    existing = {
        "name": state.name,
        "reason": state.reason,
        "preferred_time": state.preferred_time,
    }
    return (
        "Tu es un(e) réceptionniste pour une clinique. Analyse le message du patient en FRANÇAIS et "
        "extrait les champs demandés. Réponds STRICTEMENT en JSON, sans texte autour.\n"
        "Champs à extraire: name (nom complet), reason (motif), preferred_time (préférence de date/heure en texte libre).\n"
        "Si un champ n'est pas présent, mets-le à null. N'invente pas.\n"
        f"Contexte (déjà connu, peut être null): {json.dumps(existing, ensure_ascii=False)}\n"
        f"Message: {text}\n"
        "Réponse JSON attendue (exemple): {\"name\":\"Jean Dupont\",\"reason\":\"douleur dentaire\",\"preferred_time\":\"mardi prochain matin\"}"
    )


SYSTEM_INSTRUCTIONS = (
    "Tu es un(e) réceptionniste pour une clinique."
    " Extrait strictement les champs demandés et n'invente rien."
)


def build_messages(text: str, state: SessionState) -> List[Dict[str, str]]:
    existing = {
        "name": state.name,
        "reason": state.reason,
        "preferred_time": state.preferred_time,
    }
    user = (
        "Analyse le message du patient en FRANÇAIS et retourne UNIQUEMENT un JSON avec"
        " les clés: name, reason, preferred_time. Mets une clé à null si absente.\n"
        f"Contexte (peut contenir des null): {json.dumps(existing, ensure_ascii=False)}\n"
        f"Message: {text}"
    )
    return [
        {"role": "system", "content": SYSTEM_INSTRUCTIONS},
        {"role": "user", "content": user},
    ]


def merge_extracted(state: SessionState, extracted: Dict[str, Optional[str]]) -> SessionState:
    state.name = state.name or _clean(extracted.get("name"))
    state.reason = state.reason or _clean(extracted.get("reason"))
    state.preferred_time = state.preferred_time or _clean(extracted.get("preferred_time"))
    return state


def compute_missing(state: SessionState) -> List[str]:
    missing: List[str] = []
    if not state.name:
        missing.append("name")
    if not state.reason:
        missing.append("reason")
    if not state.preferred_time:
        missing.append("preferred_time")
    return missing


def compose_followup(state: SessionState) -> str:
    missing = compute_missing(state)
    if not missing:
        # Confirmation
        return (
            "Merci. J’ai noté:\n"
            f"- Nom: {state.name}\n"
            f"- Raison: {state.reason}\n"
            f"- Préférence: {state.preferred_time}"
            + (f" (≈ {state.preferred_time_iso})" if getattr(state, "preferred_time_iso", None) else "")
            + "\n"
            "Je regarde les disponibilités et je reviens vers vous."
        )
    # Ask for the next missing field
    field = missing[0]
    if field == "name":
        return "Merci. Pouvez-vous me donner votre nom complet, s’il vous plaît ?"
    if field == "reason":
        return "Merci. Quelle est la raison de votre visite ?"
    return "Merci. Quelle est votre préférence de date/heure ? (ex.: mardi prochain matin)"


def try_parse_json(text: str) -> Optional[Dict[str, Optional[str]]]:
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return {
                "name": _clean(data.get("name")),
                "reason": _clean(data.get("reason")),
                "preferred_time": _clean(data.get("preferred_time")),
            }
    except Exception:
        return None
    return None


def _clean(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    s = str(value).strip()
    return s or None
