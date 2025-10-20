from agents.session import SessionState
from agents.conversation import compute_missing, compose_followup, merge_extracted


def test_missing_and_followup_prompt_order():
    s = SessionState(from_waid="+1000")
    assert compute_missing(s) == ["name", "reason", "preferred_time"]
    assert "nom" in compose_followup(s).lower()

    s = merge_extracted(s, {"name": "Alice", "reason": None, "preferred_time": None})
    assert compute_missing(s) == ["reason", "preferred_time"]
    assert "raison" in compose_followup(s).lower()

    s = merge_extracted(s, {"reason": "Douleur dentaire", "preferred_time": None})
    assert compute_missing(s) == ["preferred_time"]
    assert "préférence" in compose_followup(s).lower()

    s = merge_extracted(s, {"preferred_time": "Mardi matin"})
    assert compute_missing(s) == []
    out = compose_followup(s)
    assert "Merci" in out and "Nom" in out and "Raison" in out and "Préférence" in out

