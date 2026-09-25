"""Diagnostic sensor: last access time and exposed event count per flow."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import ATTR_EVENT_COUNT, ATTR_LAST_ACCESSED, DOMAIN, SIGNAL_FLOW_ACCESSED


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the diagnostic sensor for this flow."""
    async_add_entities([CalendarShareLastAccessedSensor(entry)])


class CalendarShareLastAccessedSensor(SensorEntity):
    """Timestamp of the last time this flow's feed was fetched."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_should_poll = False

    def __init__(self, entry: ConfigEntry) -> None:
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_last_accessed"
        self._attr_name = f"{entry.title} last accessed"
        self._attr_native_value = None
        self._attr_extra_state_attributes: dict[str, Any] = {ATTR_EVENT_COUNT: 0}

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                SIGNAL_FLOW_ACCESSED.format(entry_id=self._entry.entry_id),
                self._handle_accessed,
            )
        )

    @callback
    def _handle_accessed(self, data: dict[str, Any]) -> None:
        self._attr_native_value = data[ATTR_LAST_ACCESSED]
        self._attr_extra_state_attributes = {
            ATTR_EVENT_COUNT: data[ATTR_EVENT_COUNT]
        }
        self.async_write_ha_state()

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=self._entry.title,
            entry_type=DeviceEntryType.SERVICE,
        )
