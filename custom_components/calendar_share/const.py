"""Constants for the Calendar Share integration."""
from __future__ import annotations

DOMAIN = "calendar_share"

CONF_CALENDAR_ENTITY_ID = "calendar_entity_id"
CONF_TOKEN = "token"
CONF_DAYS_AHEAD = "days_ahead"
CONF_REGENERATE_TOKEN = "regenerate_token"

DEFAULT_DAYS_AHEAD = 30
MIN_DAYS_AHEAD = 1
MAX_DAYS_AHEAD = 365

TOKEN_BYTES = 32

API_URL_PATTERN = "/api/calendar_share/{entry_id}"

ATTR_LAST_ACCESSED = "last_accessed"
ATTR_EVENT_COUNT = "event_count"

SIGNAL_FLOW_ACCESSED = f"{DOMAIN}_flow_accessed_{{entry_id}}"
