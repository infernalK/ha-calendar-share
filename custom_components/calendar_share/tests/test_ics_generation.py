"""Tests for ICS generation, independent of Home Assistant's HTTP stack."""
from __future__ import annotations

from custom_components.calendar_share.http_view import CalendarShareView


def _ics_text(entity_id: str, events: list[dict]) -> str:
    return CalendarShareView._build_ics(entity_id, events).decode("utf-8")


def test_simple_timed_event():
    events = [
        {
            "uid": "abc123",
            "summary": "Réunion parents-profs",
            "start": "2026-10-05T14:00:00+02:00",
            "end": "2026-10-05T15:00:00+02:00",
        }
    ]
    ics = _ics_text("calendar.skolengo_enfant1", events)
    assert "BEGIN:VCALENDAR" in ics
    assert "BEGIN:VEVENT" in ics
    assert "SUMMARY:Réunion parents-profs" in ics
    assert "DTSTART" in ics
    assert "DTEND" in ics
    assert "END:VEVENT" in ics
    assert "END:VCALENDAR" in ics


def test_all_day_event_has_date_only_values():
    events = [
        {
            "uid": "day1",
            "summary": "Sortie scolaire",
            "start": "2026-10-06",
            "end": "2026-10-07",
        }
    ]
    ics = _ics_text("calendar.skolengo_enfant1", events)
    assert "DTSTART;VALUE=DATE:20261006" in ics
    assert "DTEND;VALUE=DATE:20261007" in ics


def test_multi_day_timed_event():
    events = [
        {
            "uid": "trip1",
            "summary": "Voyage scolaire",
            "start": "2026-11-02T08:00:00+01:00",
            "end": "2026-11-04T18:00:00+01:00",
        }
    ]
    ics = _ics_text("calendar.skolengo_enfant1", events)
    assert "SUMMARY:Voyage scolaire" in ics


def test_special_characters_are_escaped():
    events = [
        {
            "uid": "special1",
            "summary": "Cours; Maths, Physique\net Chimie",
            "description": "Salle A; Prof: M. Durand, Mme Martin",
            "start": "2026-10-05T08:00:00+02:00",
            "end": "2026-10-05T09:00:00+02:00",
        }
    ]
    ics = _ics_text("calendar.skolengo_enfant1", events)
    assert "SUMMARY:Cours\\; Maths\\, Physique\\net Chimie" in ics
    assert "DESCRIPTION:Salle A\\; Prof: M. Durand\\, Mme Martin" in ics


def test_uid_is_stable_and_scoped_to_entity():
    events = [
        {
            "uid": "same-source-id",
            "summary": "Cours",
            "start": "2026-10-05T08:00:00+02:00",
            "end": "2026-10-05T09:00:00+02:00",
        }
    ]
    ics_a = _ics_text("calendar.skolengo_enfant1", events)
    ics_b = _ics_text("calendar.skolengo_enfant2", events)

    uid_a = [line for line in ics_a.splitlines() if line.startswith("UID:")][0]
    uid_b = [line for line in ics_b.splitlines() if line.startswith("UID:")][0]

    assert uid_a != uid_b

    ics_a_again = _ics_text("calendar.skolengo_enfant1", events)
    uid_a_again = [
        line for line in ics_a_again.splitlines() if line.startswith("UID:")
    ][0]
    assert uid_a == uid_a_again


def test_empty_events_produces_valid_empty_calendar():
    ics = _ics_text("calendar.skolengo_enfant1", [])
    assert "BEGIN:VCALENDAR" in ics
    assert "END:VCALENDAR" in ics
    assert "BEGIN:VEVENT" not in ics
