from __future__ import annotations

from typing import List, Optional

from app.config import Settings
from agents.client import create_agents_client
from agents.datetime_fr import format_fr_human


STYLE_GUIDE = (
    "Tu es l’assistant virtuel d’un cabinet dentaire.\n"
    "RÈGLES GÉNÉRALES (toujours vraies sauf indication contraire) :\n"
    "1) Toujours vouvoyer le patient.\n"
    "2) Ton empathique, clair et professionnel.\n"
    "3) Toujours répondre en FRANÇAIS.\n"
    "4) Forme par défaut : UNE SEULE PHRASE sur UNE LIGNE, ≤ 220 caractères.\n"
    "5) Pas de salutations (pas de « bonjour »), pas de listes, pas d’émojis.\n"
    "6) Ne jamais entourer le message de guillemets.\n"
    "7) Ne pas inventer de données ; utiliser uniquement les variables fournies.\n"
)


def _sanitize_oneline(text: str, max_len: int = 220) -> str:
    t = (text or "").replace("\n", " ").replace("\r", " ").strip()
    # enlever guillemets englobants éventuels
    if (t.startswith('"') and t.endswith('"')) or (t.startswith("'") and t.endswith("'")):
        t = t[1:-1].strip()
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
    asked_list = already_asked or []
    asked = ", ".join(asked_list) or "aucun"
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
        "OBJECTIF :\n"
        f"- Poser UNE SEULE question polie pour obtenir {field_label}.\n"
        "- Une seule phrase sur une ligne, ≤ 220 caractères.\n"
        "- Ne pas reformuler ni redemander les champs déjà demandés.\n"
        "- Ne pas poser d’autres questions.\n"
        "- Ne pas entourer la phrase de guillemets, pas d’émojis.\n"
        "Répondre uniquement avec le texte du message."
    )

    out = _call_openai(settings, system, user)
    return _sanitize_oneline(out or "") if out else None



def confirmation(
    settings: Settings,
    *,
    name: Optional[str],
    reason: Optional[str],
    preferred_time_iso: str,
) -> Optional[str]:
    system = STYLE_GUIDE
    date_h = format_fr_human(preferred_time_iso)
    user = (
        f"Variables:\n- date_long: {date_h}\n- nom: {name or '—'}\n- raison: {reason or '—'}\n\n"
        "OBJECTIF :\n"
        "- Rédiger une confirmation de réservation claire.\n"
        "- Inclure l’idée : « Vous recevrez un rappel 24h avant. ».\n"
        "- Une seule phrase sur une ligne, ≤ 220 caractères.\n"
        "- Ne pas entourer la phrase de guillemets, pas d’émojis.\n"
        "Ne renvoyez que le texte du message."
    )
    out = _call_openai(settings, system, user)
    return _sanitize_oneline(out or "") if out else None



def alternatives(settings: Settings, *, options_iso: List[str]) -> Optional[str]:
    system = STYLE_GUIDE
    items = [f"{i+1}) {format_fr_human(iso)}" for i, iso in enumerate(options_iso)]
    listing = "\n".join(items)

    user = (
        "Vous allez proposer des créneaux disponibles au patient.\n\n"
        "RÈGLES SPÉCIFIQUES À CETTE TÂCHE (prioritaires sur les règles générales) :\n"
        "- Utiliser plusieurs lignes.\n"
        "- Première ligne suggérée : « Voici des créneaux disponibles : ».\n"
        "- Ensuite, liste numérotée, un créneau par ligne, en utilisant exactement la liste ci-dessous.\n"
        "- Terminer par : « Répondez 1 ou 2 pour choisir. ».\n"
        "- Pas d’autre texte, pas d’émojis, pas de guillemets.\n\n"
        f"Liste des créneaux à utiliser telle quelle :\n{listing}\n\n"
        "Ne renvoyez que le texte du message."
    )

    out = _call_openai(settings, system, user)
    # ici on NE passe PAS par _sanitize_oneline, car on veut garder les retours à la ligne
    return out.strip() if out else None



def greeting(settings: Settings) -> Optional[str]:
    system = STYLE_GUIDE
    user = (
        "Composez un message d’accueil concis pour WhatsApp.\n"
        "CONTENU OBLIGATOIRE :\n"
        "- Consentement pour l’usage des informations afin de gérer les rendez-vous.\n"
        "- Mention que l’on peut répondre STOP pour se désinscrire.\n"
        "- Mentionner d’appeler le 112 en cas d’urgence vitale.\n"
        "CONTRAINTES :\n"
        "- Une seule phrase sur une ligne, ≤ 220 caractères.\n"
        "- Pas de salutations type « bonjour », pas d’émojis, pas de guillemets.\n"
        "Répondre uniquement avec le texte du message."
    )
    out = _call_openai(settings, system, user)
    return _sanitize_oneline(out or "") if out else None



def id_ack(
    settings: Settings,
    *,
    name: Optional[str],
    dob: Optional[str],
    email: Optional[str],
) -> Optional[str]:
    system = STYLE_GUIDE
    user = (
        "Composez un accusé de réception court et empathique confirmant l’identité.\n"
        f"Données fournies : nom={name or '—'}, dob={dob or '—'} (JJ/MM/AAAA), email={email or '—'}.\n"
        "OBJECTIF :\n"
        "- Confirmer explicitement ces trois éléments.\n"
        "- Terminer en demandant le type de rendez-vous souhaité.\n"
        "CONTRAINTES :\n"
        "- Une seule phrase sur une ligne, ≤ 220 caractères.\n"
        "- Ne pas entourer la phrase de guillemets, pas d’émojis.\n"
        "Répondre uniquement avec le texte du message."
    )
    out = _call_openai(settings, system, user)
    return _sanitize_oneline(out or "") if out else None

