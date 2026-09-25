"""Constants for the Calendar Share integration."""
from __future__ import annotations

DOMAIN = "calendar_share"

CONF_CALENDAR_ENTITY_ID = "calendar_entity_id"
CONF_TOKEN = "token"
CONF_DAYS_AHEAD = "days_ahead"
CONF_DAYS_BEHIND = "days_behind"
CONF_REGENERATE_TOKEN = "regenerate_token"

# Wide enough that a school-year-bound calendar (or anything similar) is
# exposed in full out of the box, without anyone having to tune these:
# most calendar sources that bound themselves at all (school years,
# academic terms, ...) fit comfortably within ~13 months either side of
# today. Still finite so a feed can't grow unbounded against a calendar
# entity with years of recurring events.
DEFAULT_DAYS_AHEAD = 400
DEFAULT_DAYS_BEHIND = 400
MIN_DAYS_AHEAD = 0
MAX_DAYS_AHEAD = 3650
MIN_DAYS_BEHIND = 0
MAX_DAYS_BEHIND = 3650

TOKEN_BYTES = 32

API_URL_PATTERN = "/api/calendar_share/{token}"

ATTR_LAST_ACCESSED = "last_accessed"
ATTR_EVENT_COUNT = "event_count"

SIGNAL_FLOW_ACCESSED = f"{DOMAIN}_flow_accessed_{{entry_id}}"
