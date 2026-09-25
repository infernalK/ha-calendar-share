"""Tests for the HTTP view: token validation and response shape."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from homeassistant.core import ServiceCall, SupportsResponse

from custom_components.calendar_share.const import DOMAIN
from custom_components.calendar_share.http_view import CalendarShareView


class _FakeEntry:
    def __init__(
        self, entry_id: str, entity_id: str, token: str, days_ahead: int = 30
    ) -> None:
        self.entry_id = entry_id
        self.data = {"calendar_entity_id": entity_id, "token": token}
        self.options = {"days_ahead": days_ahead}


def _make_request() -> MagicMock:
    return MagicMock()


@pytest.mark.asyncio
async def test_unknown_token_returns_403(hass):
    hass.data[DOMAIN] = {
        "entry1": {
            "entry": _FakeEntry("entry1", "calendar.foo", "correct-token")
        }
    }
    view = CalendarShareView(hass)
    response = await view.get(_make_request(), "wrong-token")
    assert response.status == 403


@pytest.mark.asyncio
async def test_no_flows_configured_returns_403(hass):
    view = CalendarShareView(hass)
    response = await view.get(_make_request(), "whatever")
    assert response.status == 403


@pytest.mark.asyncio
async def test_correct_token_returns_ics(hass):
    hass.data[DOMAIN] = {
        "entry1": {
            "entry": _FakeEntry("entry1", "calendar.foo", "correct-token")
        }
    }

    async def fake_get_events(call: ServiceCall) -> dict:
        return {
            "calendar.foo": {
                "events": [
                    {
                        "uid": "e1",
                        "summary": "Test event",
                        "start": "2026-10-05T08:00:00+02:00",
                        "end": "2026-10-05T09:00:00+02:00",
                    }
                ]
            }
        }

    hass.services.async_register(
        "calendar",
        "get_events",
        fake_get_events,
        supports_response=SupportsResponse.ONLY,
    )

    view = CalendarShareView(hass)
    response = await view.get(_make_request(), "correct-token")

    assert response.status == 200
    assert response.content_type == "text/calendar"
    body = response.body.decode("utf-8")
    assert "BEGIN:VCALENDAR" in body
    assert "SUMMARY:Test event" in body


@pytest.mark.asyncio
async def test_correct_token_picks_the_matching_flow_among_several(hass):
    hass.data[DOMAIN] = {
        "entry1": {
            "entry": _FakeEntry("entry1", "calendar.foo", "token-one")
        },
        "entry2": {
            "entry": _FakeEntry("entry2", "calendar.bar", "token-two")
        },
    }

    async def fake_get_events(call: ServiceCall) -> dict:
        entity_id = call.data["entity_id"]
        return {entity_id: {"events": []}}

    hass.services.async_register(
        "calendar",
        "get_events",
        fake_get_events,
        supports_response=SupportsResponse.ONLY,
    )

    view = CalendarShareView(hass)
    response = await view.get(_make_request(), "token-two")
    assert response.status == 200


@pytest.mark.asyncio
async def test_token_never_appears_in_error_log(hass, caplog):
    hass.data[DOMAIN] = {
        "entry1": {
            "entry": _FakeEntry("entry1", "calendar.foo", "super-secret-token")
        }
    }
    view = CalendarShareView(hass)
    await view.get(_make_request(), "attacker-guess")

    assert "super-secret-token" not in caplog.text
    assert "attacker-guess" not in caplog.text
