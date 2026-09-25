"""The Calendar Share integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .http_view import CalendarShareView

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Calendar Share from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    domain_data = hass.data[DOMAIN]
    is_first_entry = "view_registered" not in domain_data

    domain_data[entry.entry_id] = {"entry": entry}

    if is_first_entry:
        hass.http.register_view(CalendarShareView(hass))
        domain_data["view_registered"] = True

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update, including token regeneration."""
    await hass.config_entries.async_reload(entry.entry_id)
