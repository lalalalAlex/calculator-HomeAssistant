from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

import logging

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'calculator'
PLATFORMS = ['number', 'select', 'sensor']


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})

    hass.data[DOMAIN][entry.entry_id] = {
        'first_number': entry.data.get('num1', 0),
        'second_number': entry.data.get('num2', 0),
        'operation': entry.data.get('operation', '+'),
        'result': 0,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok