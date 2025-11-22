from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Union, Dict, Any

from app.config import Settings
import logging
from agents.datetime_fr import parse_preferred_time_fr, format_fr_human
from agents.session import SessionState
from agents.replygen import greeting as gen_greeting, id_ack as gen_id_ack, confirmation as gen_confirmation
from connectors.calendar.provider import get_calendar_provider

logger = logging.getLogger(__name__)


def _is_weekend(dt: datetime) -> bool:
    return dt.weekday() >= 5


def _slots_from_preference(start_iso: str, *, tz: str, plage: Optional[str]) -> List[datetime]:
    base = datetime.fromisoformat(start_iso)
    hours = [9, 14, 18]
    if plage:
        pl = plage.lower()
        if "matin" in pl:
            hours = [9, 10, 11]
        elif "après" in pl or "apres" in pl:
            hours = [14, 15, 16]
        elif "soir" in pl:
            hours = [18, 19, 17]
    out: List[datetime] = []
    # try same day, then subsequent business days
    day = base.replace(hour=hours[0], minute=0, second=0, microsecond=0)
    for d in range(0, 10):
        cur = day + timedelta(days=d)
        if _is_weekend(cur):
            continue
        for h in hours:
            candidate = cur.replace(hour=h)
            out.append(candidate)
    return out


def _offer_three_slots(settings: Settings, st: SessionState, start_iso: str) -> Tuple[List[str], List[str]]:
    provider = get_calendar_provider(settings)
    iso_list: List[str] = []
    labels: List[str] = []
    if provider is None:
        # fallback: offer next three business-day 10:00 slots
        base = datetime.fromisoformat(start_iso)
        day = base
        while len(iso_list) < 3:
            day += timedelta(days=1)
            if _is_weekend(day):
                continue
            slot = day.replace(hour=10, minute=0, second=0, microsecond=0)
            iso_list.append(slot.isoformat())
            labels.append(format_fr_human(slot.isoformat()))
        return iso_list, labels

    plage = st.plage_horaire
    for dt in _slots_from_preference(start_iso, tz=settings.clinic_tz, plage=plage):
        if provider.is_available(dt, duration_min=30):
            iso_list.append(dt.isoformat())
            labels.append(format_fr_human(dt.isoformat()))
            if len(iso_list) >= 3:
                break
    # If still not enough, keep scanning next business days at 10:00
    day = datetime.fromisoformat(start_iso)
    while len(iso_list) < 3:
        day += timedelta(days=1)
        if _is_weekend(day):
            continue
        dt = day.replace(hour=10, minute=0, second=0, microsecond=0)
        if provider.is_available(dt, duration_min=30):
            iso_list.append(dt.isoformat())
            labels.append(format_fr_human(dt.isoformat()))
    return iso_list, labels


def handle_message(text: str, st: SessionState, settings: Settings) -> Optional[Union[str, Dict[str, Any]]]:
    t = (text or "").strip()
    low = t.lower()

    # STOP handling
    if low == "stop":
        st.stop_opt_out = True
        return "D’accord, nous ne vous enverrons plus de messages."
    if st.stop_opt_out:
        return None

    # Entry greeting
    if not st.stage:
        st.stage = "identite"
        if getattr(settings, "agent_generate_replies", False) and getattr(settings, "agent_generate_greeting", False):
            out = gen_greeting(settings)
            if out:
                return out
        return (
            "Bonjour 👋 Vous êtes en contact avec l’assistant du cabinet dentaire. "
            "Je peux vous aider à prendre, décaler ou annuler un rendez-vous. "
            "En poursuivant, vous acceptez l’utilisation de vos informations pour gérer vos rendez-vous. "
            "Tapez STOP pour ne plus recevoir de messages. En cas d’urgence vitale, appelez le 112.\n\n"
            "Pour commencer, indiquez Nom + Prénom, votre date de naissance (JJ/MM/AAAA) et votre email. "
            "En savoir plus: https://mediflow-ai.vercel.app/"
        )

    # Cancel / reschedule intents
    if any(k in low for k in ["annuler", "annulation"]):
        st.stage = "annuler_confirm"
        return "Je peux annuler votre rendez-vous. Confirmez OUI pour annuler."
    if any(k in low for k in ["décaler", "decaler", "replanifier", "changer"]):
        st.stage = "preferences"
        return "D’accord, regardons d’autres créneaux. Avez-vous une préférence de jour ou d’horaire ?"

    # Identity stage (expects: name + DOB + email)
    if st.stage == "identite":
        m_dob = re.search(r"(\d{2}/\d{2}/\d{4})", t)
        if m_dob:
            st.dob = m_dob.group(1)
        m_email = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", t)
        if m_email:
            st.email = m_email.group(0)
        # Derive name by removing dob and email
        tmp = t
        if m_dob:
            tmp = tmp.replace(st.dob or "", " ")
        if m_email:
            tmp = tmp.replace(st.email or "", " ")
        name = tmp.strip()
        if name:
            st.name = name
        if not st.name or not st.dob or not st.email:
            st.failed_identity += 1
            if st.failed_identity >= 2:
                st.stage = "handoff"
                return "Je vous mets en relation avec l’équipe. Merci de patienter."
            # Targeted re-asks
            if not st.name and (st.dob or st.email):
                return "Merci. Indiquez votre Nom + Prénom, s’il vous plaît."
            if not st.dob and (st.name or st.email):
                return "Merci. Indiquez votre date de naissance (JJ/MM/AAAA), s’il vous plaît."
            if not st.email and (st.name or st.dob):
                return "Merci. Indiquez votre adresse email, s’il vous plaît."
            return "Pour commencer, indiquez Nom + Prénom, votre date de naissance (JJ/MM/AAAA) et votre email."
        st.stage = "service"
        ack = None
        if getattr(settings, "agent_generate_replies", False) and getattr(settings, "agent_generate_id_ack", False):
            ack = gen_id_ack(settings, name=st.name, dob=st.dob, email=getattr(st, "email", None))
        if not ack:
            ack = f"Merci, j’ai bien noté: {st.name} ({st.dob}) – {st.email}. Quel type de rendez-vous souhaitez-vous ?"
        return {
            "type": "service_buttons",
            "text": (ack + "\n" "1) Contrôle / prévention\n2) Détartrage\n3) Douleur / urgence"),
            "buttons": [
                {"id": "service_controle", "title": "Contrôle"},
                {"id": "service_detartrage", "title": "Détartrage"},
                {"id": "service_urgence", "title": "Urgence"},
            ],
        }

    # Service stage
    if st.stage == "service":
        mapping = {
            "1": "controle",
            "2": "detartrage",
            "3": "urgence",
            "4": "autre",
        }
        chosen = None
        if t in mapping:
            chosen = mapping[t]
        else:
            if any(k in low for k in ["contrôle", "controle"]):
                chosen = "controle"
            elif "détartrage" in low or "detartrage" in low:
                chosen = "detartrage"
            elif "douleur" in low or "urgence" in low:
                chosen = "urgence"
            elif "autre" in low:
                chosen = "autre"
        if not chosen:
            return (
                "Quel type de rendez-vous souhaitez-vous ?\n"
                "1) Contrôle / prévention\n2) Détartrage\n3) Douleur / urgence"
            )
        st.service = chosen
        if chosen == "urgence":
            st.stage = "triage"
            return (
                "Sur une échelle de 0 à 10, à combien évaluez-vous la douleur ? "
                "Y a-t-il gonflement, fièvre ou traumatisme récent ?"
            )
        st.stage = "preferences"
        return f"Très bien {st.name or ''}. Avez-vous une préférence de jour (ex. demain, lundi prochain) et d’horaire (matin / après-midi / soir) ?"

    # Triage stage
    if st.stage == "triage":
        score = None
        m = re.search(r"(\d{1,2})", low)
        if m:
            try:
                score = int(m.group(1))
            except Exception:
                score = None
        red = any(k in low for k in ["gonflement", "fièvre", "fievre", "traumatisme"])
        st.douleur_score = score
        st.red_flags = red
        if (score is not None and score >= 8) or red:
            st.stage = "handoff"
            return "Je vous mets en relation avec l’équipe. Merci de patienter."
        st.stage = "preferences"
        return f"Merci {st.name or ''}. Avez-vous une préférence de jour et d’horaire (matin / après-midi / soir) ?"

    # Preferences stage
    if st.stage == "preferences":
        st.date_cible_text = t
        if any(k in low for k in ["matin", "après-midi", "apres-midi", "soir"]):
            st.plage_horaire = "matin" if "matin" in low else ("après-midi" if ("après" in low or "apres" in low) else "soir")
        # parse date target
        try:
            parsed = parse_preferred_time_fr(st.date_cible_text or t, tz=settings.clinic_tz)
            if parsed and parsed.iso:
                st.preferred_time_iso = parsed.iso
        except Exception:
            pass
        if not st.preferred_time_iso:
            return "Pouvez-vous préciser un jour (ex. demain, lundi prochain) et un horaire (matin / après-midi / soir) ?"
        # Offer three slots
        st.stage = "offer_slots"
        iso_list, labels = _offer_three_slots(settings, st, st.preferred_time_iso)
        st.slots_offered = iso_list[:3]
        # Text-only offer (interactive buttons removed)
        items = [f"{i+1}) {labels[i]}" for i in range(min(3, len(labels)))]
        return "Voici des créneaux disponibles : " + ", ".join(items) + ". Répondez 1, 2 ou 3."

    if st.stage == "offer_slots" or st.stage == "await_choice":
        st.stage = "await_choice"
        if low.startswith("1") or low.startswith("2") or low.startswith("3"):
            idx = 0 if low.startswith("1") else (1 if low.startswith("2") else 2)
            if st.slots_offered and 0 <= idx < len(st.slots_offered):
                st.preferred_time_iso = st.slots_offered[idx]
                st.stage = "confirm"
                return "Parfait. Merci de confirmer OUI pour finaliser la réservation."
        return "Répondez 1, 2 ou 3 pour choisir un créneau, ou dites Décaler pour d’autres options."

    if st.stage == "confirm":
        if low.strip() == "oui":
            # Finalize booking
            if not st.preferred_time_iso:
                # Should not happen, re-enter preferences
                st.stage = "preferences"
                return "Merci. Précisez un jour et un horaire (matin / après-midi / soir)."
            provider = get_calendar_provider(settings)
            try:
                start = datetime.fromisoformat(st.preferred_time_iso)
                # Resolve calendar id per channel if overrides are set
                try:
                    ch = getattr(st, 'channel', None)
                    cal_id = None
                    if ch == 'web_demo' and getattr(settings, 'calendar_id_web_demo', None):
                        cal_id = settings.calendar_id_web_demo
                    elif ch == 'whatsapp' and getattr(settings, 'calendar_id_whatsapp', None):
                        cal_id = settings.calendar_id_whatsapp
                    if cal_id and provider and hasattr(provider, '_calendar_id'):
                        setattr(provider, '_calendar_id', cal_id)
                except Exception:
                    pass
                # Prepare title/desc and idempotency key
                ch = getattr(st, 'channel', None) or 'whatsapp'
                idem = f"{ch}:{st.from_waid}:{st.preferred_time_iso}"
                base_title = f"Mediflow - {st.name or ''} 🦷".strip()
                title = base_title if ch != 'web_demo' else f"DEMO — {base_title}"
                base_desc = f"Motif: {st.reason or ''}".strip()
                desc = base_desc if ch != 'web_demo' else f"Simulation — pas un vrai rendez-vous. {base_desc}"
                if provider and provider.is_available(start, duration_min=30):
                    evt = provider.create_event(
                        start,
                        duration_min=30,
                        title=title,
                        description=desc,
                        patient_phone=st.from_waid,
                        patient_name=st.name,
                        patient_email=getattr(st, "email", None),
                        idempotency_key=idem,
                    )
                    st.event_id = evt.id
                    try:
                        logger.info(
                            "booking_created",
                            extra={
                                "channel": ch,
                                "event_id": evt.id,
                                "start": start.isoformat(),
                                "idempotency_key": idem,
                                "email_sent": bool(getattr(settings, "calendar_send_updates", False) and getattr(st, "email", None)),
                            },
                        )
                    except Exception:
                        pass
                # Confirmation message: model-polished or templated
                reply = None
                if getattr(settings, "agent_generate_replies", False) and getattr(settings, "agent_generate_confirmations", True):
                    reply = gen_confirmation(settings, name=st.name, reason=st.reason, preferred_time_iso=st.preferred_time_iso)
                if not reply:
                    extra = ""
                    if getattr(settings, "calendar_send_updates", False) and getattr(st, "email", None):
                        extra = " Une invitation vous a été envoyée par email."
                    reply = (
                        "Parfait 👍 Votre rendez-vous est confirmé le "
                        f"{format_fr_human(st.preferred_time_iso)}. "
                        "Vous recevrez un rappel 24h avant." + extra
                    )
                return reply
            finally:
                # Move to a terminal stage
                st.stage = "booked"
        # Not an explicit OUI
        return "Confirmez OUI pour finaliser, ou dites Décaler pour d’autres options."

    if st.stage == "annuler_confirm":
        if low.strip() == "oui":
            st.stage = "annule"
            return "Votre rendez-vous a été annulé."
        return "Confirmez OUI pour annuler, ou Prendre / Décaler sinon."

    if st.stage == "handoff":
        return "Je vous mets en relation avec l’équipe. Merci de patienter."

    # Fallback menu
    return "Je n’ai pas bien compris. Voulez-vous Prendre, Décaler ou Annuler un rendez-vous ?"
