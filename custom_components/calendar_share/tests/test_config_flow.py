"""Tests for the config and options flows."""
from __future__ import annotations

from unittest.mock import patch

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType

from custom_components.calendar_share.const import (
    CONF_CALENDAR_ENTITY_ID,
    CONF_DAYS_AHEAD,
    CONF_DAYS_BEHIND,
    CONF_FULL_CALENDAR,
    CONF_REGENERATE_TOKEN,
    CONF_TOKEN,
    DEFAULT_DAYS_AHEAD,
    DEFAULT_DAYS_BEHIND,
    DEFAULT_FULL_CALENDAR,
    DOMAIN,
)


async def test_abort_when_no_calendars(hass):
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "no_calendars"


async def test_full_flow_creates_entry_with_token_and_shows_url(
    hass, mock_calendar_state
):
    with patch(
        "custom_components.calendar_share.config_flow.get_url",
        return_value="https://ha.example.com",
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "user"

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_CALENDAR_ENTITY_ID: mock_calendar_state},
        )
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "confirm"
        assert "https://ha.example.com/api/calendar_share/" in (
            result["description_placeholders"]["url"]
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {}
        )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_CALENDAR_ENTITY_ID] == mock_calendar_state
    assert len(result["data"][CONF_TOKEN]) > 20
    assert result["options"][CONF_DAYS_AHEAD] == DEFAULT_DAYS_AHEAD
    assert result["options"][CONF_DAYS_BEHIND] == DEFAULT_DAYS_BEHIND
    assert result["options"][CONF_FULL_CALENDAR] == DEFAULT_FULL_CALENDAR


async def test_two_flows_for_same_calendar_get_different_tokens(
    hass, mock_calendar_state
):
    with patch(
        "custom_components.calendar_share.config_flow.get_url",
        return_value="https://ha.example.com",
    ):
        tokens = []
        for _ in range(2):
            result = await hass.config_entries.flow.async_init(
                DOMAIN, context={"source": config_entries.SOURCE_USER}
            )
            result = await hass.config_entries.flow.async_configure(
                result["flow_id"],
                {CONF_CALENDAR_ENTITY_ID: mock_calendar_state},
            )
            result = await hass.config_entries.flow.async_configure(
                result["flow_id"], {}
            )
            tokens.append(result["data"][CONF_TOKEN])

    assert tokens[0] != tokens[1]


async def test_regenerate_token_invalidates_old_token(hass, mock_calendar_state):
    with patch(
        "custom_components.calendar_share.config_flow.get_url",
        return_value="https://ha.example.com",
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_CALENDAR_ENTITY_ID: mock_calendar_state}
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {}
        )
        entry = hass.config_entries.async_entries(DOMAIN)[0]
        old_token = entry.data[CONF_TOKEN]

        options_result = await hass.config_entries.options.async_init(
            entry.entry_id
        )
        options_result = await hass.config_entries.options.async_configure(
            options_result["flow_id"],
            {
                CONF_FULL_CALENDAR: False,
                CONF_DAYS_AHEAD: 30,
                CONF_DAYS_BEHIND: 30,
                CONF_REGENERATE_TOKEN: True,
            },
        )

    assert options_result["type"] == FlowResultType.FORM
    assert options_result["step_id"] == "show_new_token"
    new_token = entry.data[CONF_TOKEN]
    assert new_token != old_token


async def test_full_calendar_option_can_be_enabled(hass, mock_calendar_state):
    with patch(
        "custom_components.calendar_share.config_flow.get_url",
        return_value="https://ha.example.com",
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_CALENDAR_ENTITY_ID: mock_calendar_state}
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {}
        )
        entry = hass.config_entries.async_entries(DOMAIN)[0]

        options_result = await hass.config_entries.options.async_init(
            entry.entry_id
        )
        options_result = await hass.config_entries.options.async_configure(
            options_result["flow_id"],
            {
                CONF_FULL_CALENDAR: True,
                CONF_DAYS_AHEAD: 30,
                CONF_DAYS_BEHIND: 30,
            },
        )

    assert options_result["type"] == FlowResultType.CREATE_ENTRY
    assert entry.options[CONF_FULL_CALENDAR] is True
