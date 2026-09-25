"""HTTP view exposing a single calendar as an unauthenticated iCalendar feed.

The URL itself carries a per-flow secret token (query parameter) that is
validated in constant time. No Home Assistant Authorization header is
required or accepted, which is what lets native mobile/desktop calendar
apps subscribe directly. Only GET is exposed and only calendar.get_events
is ever called - this view can never mutate state.
"""
from __future__ import annotations

import hashlib
import logging
import secrets
from datetime import datetime, timedelta

from aiohttp import web
from homeassistant.components.http import HomeAssistantView
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.util import dt as dt_util
from icalendar import Calendar, Event

from .const import (
    ATTR_EVENT_COUNT,
    ATTR_LAST_ACCESSED,
    CONF_CALENDAR_ENTITY_ID,
    CONF_DAYS_AHEAD,
    CONF_TOKEN,
    DEFAULT_DAYS_AHEAD,
    DOMAIN,
    SIGNAL_FLOW_ACCESSED,
)

_LOGGER = logging.getLogger(__name__)


class CalendarShareView(HomeAssistantView):
    """Serve GET /api/calendar_share/{entry_id}?token=... as text/calendar."""

    url = "/api/calendar_share/{entry_id}"
    name = "api:calendar_share"
    requires_auth = False

    def __init__(self, hass: HomeAssistant) -> None:
        self._hass = hass

    async def get(self, request: web.Request, entry_id: str) -> web.Response:
        domain_data = self._hass.data.get(DOMAIN, {})
        flow = domain_data.get(entry_id)

        # Do not log the presented token, valid or not.
        if flow is None:
            _LOGGER.info("Calendar share request for unknown flow id")
            return web.Response(status=404)

        entry = flow["entry"]
        expected_token: str = entry.data[CONF_TOKEN]
        presented_token = request.query.get("token", "")

        if not secrets.compare_digest(presented_token, expected_token):
            _LOGGER.warning(
                "Calendar share request for %s rejected: invalid token", entry_id
            )
            return web.Response(status=403)

        entity_id: str = entry.data[CONF_CALENDAR_ENTITY_ID]
        days_ahead: int = entry.options.get(CONF_DAYS_AHEAD, DEFAULT_DAYS_AHEAD)

        events = await self._async_get_events(entity_id, days_ahead)
        ics_body = self._build_ics(entity_id, events)

        async_dispatcher_send(
            self._hass,
            SIGNAL_FLOW_ACCESSED.format(entry_id=entry_id),
            {
                ATTR_LAST_ACCESSED: dt_util.utcnow(),
                ATTR_EVENT_COUNT: len(events),
            },
        )

        return web.Response(
            body=ics_body,
            content_type="text/calendar",
            charset="utf-8",
        )

    async def _async_get_events(
        self, entity_id: str, days_ahead: int
    ) -> list[dict]:
        now = dt_util.now()
        start = now - timedelta(days=1)
        end = now + timedelta(days=days_ahead)

        response = await self._hass.services.async_call(
            "calendar",
            "get_events",
            {
                "entity_id": entity_id,
                "start_date_time": start.isoformat(),
                "end_date_time": end.isoformat(),
            },
            blocking=True,
            return_response=True,
        )
        return response.get(entity_id, {}).get("events", [])

    @staticmethod
    def _build_ics(entity_id: str, events: list[dict]) -> bytes:
        calendar = Calendar()
        calendar.add("prodid", "-//Calendar Share//Home Assistant//EN")
        calendar.add("version", "2.0")
        calendar.add("calscale", "GREGORIAN")
        calendar.add("x-wr-timezone", "Europe/Paris")

        for event in events:
            calendar.add_component(_event_to_vevent(entity_id, event))

        return calendar.to_ical()


def _event_to_vevent(entity_id: str, event: dict) -> Event:
    """Convert a calendar.get_events event dict into an icalendar Event."""
    vevent = Event()

    raw_uid = event.get("uid") or f"{event.get('summary', '')}|{event['start']}"
    stable_uid = hashlib.sha256(f"{entity_id}:{raw_uid}".encode()).hexdigest()
    vevent.add("uid", f"{stable_uid}@calendar-share")

    vevent.add("summary", event.get("summary", ""))
    if event.get("description"):
        vevent.add("description", event["description"])
    if event.get("location"):
        vevent.add("location", event["location"])

    start = _parse_event_datetime(event["start"])
    end = _parse_event_datetime(event["end"])
    vevent.add("dtstart", start)
    vevent.add("dtend", end)
    vevent.add("dtstamp", dt_util.utcnow())

    return vevent


def _parse_event_datetime(value: str):
    """Return a date for all-day events, or a tz-aware datetime otherwise."""
    if len(value) == 10:
        return datetime.strptime(value, "%Y-%m-%d").date()
    return dt_util.parse_datetime(value) or dt_util.utcnow()
