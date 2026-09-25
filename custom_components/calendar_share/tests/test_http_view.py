"""Tests for the HTTP view: token validation and response shape."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from homeassistant.core import ServiceCall, SupportsResponse

from custom_components.calendar_share.const import DOMAIN
from custom_components.calendar_share.http_view import CalendarShareView


class _FakeEntry:
    def __init__(self, entity_id: str, token: str, days_ahead: int = 30) -> None:
        self.data = {"calendar_entity_id": entity_id, "token": token}
        self.options = {"days_ahead": days_ahead}


def _make_request(token: str | None):
    request = MagicMock()
    request.query = {"token": token} if token is not None else {}
    return request


@pytest.mark.asyncio
async def test_unknown_flow_returns_404(hass):
    view = CalendarShareView(hass)
    response = await view.get(_make_request("whatever"), "not-a-real-entry")
    assert response.status == 404


@pytest.mark.asyncio
async def test_missing_token_returns_403(hass):
    hass.data[DOMAIN] = {
        "entry1": {"entry": _FakeEntry("calendar.foo", "correct-token")}
    }
    view = CalendarShareView(hass)
    response = await view.get(_make_request(None), "entry1")
    assert response.status == 403


@pytest.mark.asyncio
async def test_wrong_token_returns_403(hass):
    hass.data[DOMAIN] = {
        "entry1": {"entry": _FakeEntry("calendar.foo", "correct-token")}
    }
    view = CalendarShareView(hass)
    response = await view.get(_make_request("wrong-token"), "entry1")
    assert response.status == 403


@pytest.mark.asyncio
async def test_correct_token_returns_ics(hass):
    hass.data[DOMAIN] = {
        "entry1": {"entry": _FakeEntry("calendar.foo", "correct-token")}
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
    response = await view.get(_make_request("correct-token"), "entry1")

    assert response.status == 200
    assert response.content_type == "text/calendar"
    body = response.body.decode("utf-8")
    assert "BEGIN:VCALENDAR" in body
    assert "SUMMARY:Test event" in body


@pytest.mark.asyncio
async def test_token_never_appears_in_error_log(hass, caplog):
    hass.data[DOMAIN] = {
        "entry1": {"entry": _FakeEntry("calendar.foo", "super-secret-token")}
    }
    view = CalendarShareView(hass)
    await view.get(_make_request("attacker-guess"), "entry1")

    assert "super-secret-token" not in caplog.text
    assert "attacker-guess" not in caplog.text
