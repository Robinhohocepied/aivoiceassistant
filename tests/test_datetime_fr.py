from datetime import datetime

from agents.datetime_fr import parse_preferred_time_fr


def test_parse_demains_matin_approx_iso():
    ref = datetime(2025, 1, 10, 16, 0)  # Friday
    out = parse_preferred_time_fr("Demain matin", now=ref)
    assert out.iso.startswith("2025-01-11T09:00")


def test_parse_weekday_and_time():
    ref = datetime(2025, 1, 10, 12, 0)  # Friday
    out = parse_preferred_time_fr("mardi 10h30", now=ref)
    # Next Tuesday is 2025-01-14
    assert out.iso.startswith("2025-01-14T10:30")

