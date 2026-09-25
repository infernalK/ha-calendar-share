"""Shared fixtures for Calendar Share tests."""
from __future__ import annotations

import pytest

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Make custom_components discoverable in every test."""
    yield


@pytest.fixture
def mock_calendar_state(hass):
    """Register a fake calendar entity state so it appears in selectors."""
    hass.states.async_set(
        "calendar.skolengo_enfant1",
        "on",
        {"friendly_name": "Skolengo - Enfant 1"},
    )
    return "calendar.skolengo_enfant1"
