"""Config flow for Calendar Share."""
from __future__ import annotations

import secrets
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.network import NoURLAvailableError, get_url
from homeassistant.helpers.selector import (
    EntitySelector,
    EntitySelectorConfig,
    NumberSelector,
    NumberSelectorConfig,
)

from .const import (
    API_URL_PATTERN,
    CONF_CALENDAR_ENTITY_ID,
    CONF_DAYS_AHEAD,
    CONF_DAYS_BEHIND,
    CONF_REGENERATE_TOKEN,
    CONF_TOKEN,
    DEFAULT_DAYS_AHEAD,
    DEFAULT_DAYS_BEHIND,
    DOMAIN,
    MAX_DAYS_AHEAD,
    MAX_DAYS_BEHIND,
    MIN_DAYS_AHEAD,
    MIN_DAYS_BEHIND,
    TOKEN_BYTES,
)


def _build_share_url(hass: HomeAssistant, token: str) -> str:
    try:
        base_url = get_url(hass, prefer_external=True, allow_internal=False)
    except NoURLAvailableError:
        base_url = get_url(hass)
    path = API_URL_PATTERN.format(token=token)
    return f"{base_url}{path}"


class CalendarShareConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Calendar Share, one flow per calendar entity."""

    VERSION = 1

    def __init__(self) -> None:
        self._entity_id: str | None = None
        self._token: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> Any:
        """Select the calendar entity to expose."""
        errors: dict[str, str] = {}

        if not self.hass.states.async_entity_ids("calendar"):
            return self.async_abort(reason="no_calendars")

        if user_input is not None:
            entity_id = user_input[CONF_CALENDAR_ENTITY_ID]
            await self.async_set_unique_id(f"{entity_id}-{secrets.token_hex(4)}")
            self._entity_id = entity_id
            self._token = secrets.token_urlsafe(TOKEN_BYTES)
            return await self.async_step_confirm()

        schema = vol.Schema(
            {
                vol.Required(CONF_CALENDAR_ENTITY_ID): EntitySelector(
                    EntitySelectorConfig(domain="calendar")
                )
            }
        )
        return self.async_show_form(
            step_id="user", data_schema=schema, errors=errors
        )

    async def async_step_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> Any:
        """Create the entry and display the share URL once."""
        assert self._entity_id is not None
        assert self._token is not None

        if user_input is not None:
            state = self.hass.states.get(self._entity_id)
            friendly_name = (
                state.attributes.get("friendly_name", self._entity_id)
                if state
                else self._entity_id
            )
            return self.async_create_entry(
                title=f"Calendar Share: {friendly_name}",
                data={
                    CONF_CALENDAR_ENTITY_ID: self._entity_id,
                    CONF_TOKEN: self._token,
                },
                options={
                    CONF_DAYS_AHEAD: DEFAULT_DAYS_AHEAD,
                    CONF_DAYS_BEHIND: DEFAULT_DAYS_BEHIND,
                },
            )

        share_url = _build_share_url(self.hass, self._token)
        return self.async_show_form(
            step_id="confirm",
            data_schema=vol.Schema({}),
            description_placeholders={"url": share_url},
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return CalendarShareOptionsFlow()


class CalendarShareOptionsFlow(OptionsFlow):
    """Handle options: sliding window and token regeneration.

    `self.config_entry` is populated automatically by the base class; it
    must not be assigned in __init__ (deprecated/removed by HA core).
    """

    def __init__(self) -> None:
        self._pending_options: dict[str, Any] = {}

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> Any:
        if user_input is not None:
            new_data = dict(self.config_entry.data)
            regenerate = user_input.pop(CONF_REGENERATE_TOKEN, False)
            self._pending_options = user_input
            if regenerate:
                new_data[CONF_TOKEN] = secrets.token_urlsafe(TOKEN_BYTES)
                self.hass.config_entries.async_update_entry(
                    self.config_entry, data=new_data
                )
                return await self.async_step_show_new_token()
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_DAYS_AHEAD,
                    default=self.config_entry.options.get(
                        CONF_DAYS_AHEAD, DEFAULT_DAYS_AHEAD
                    ),
                ): NumberSelector(
                    NumberSelectorConfig(min=MIN_DAYS_AHEAD, max=MAX_DAYS_AHEAD)
                ),
                vol.Required(
                    CONF_DAYS_BEHIND,
                    default=self.config_entry.options.get(
                        CONF_DAYS_BEHIND, DEFAULT_DAYS_BEHIND
                    ),
                ): NumberSelector(
                    NumberSelectorConfig(min=MIN_DAYS_BEHIND, max=MAX_DAYS_BEHIND)
                ),
                vol.Optional(CONF_REGENERATE_TOKEN, default=False): bool,
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)

    async def async_step_show_new_token(
        self, user_input: dict[str, Any] | None = None
    ) -> Any:
        if user_input is not None:
            return self.async_create_entry(title="", data=self._pending_options)

        token = self.config_entry.data[CONF_TOKEN]
        share_url = _build_share_url(self.hass, token)
        return self.async_show_form(
            step_id="show_new_token",
            data_schema=vol.Schema({}),
            description_placeholders={"url": share_url},
        )
