"""Custom Calculator integration."""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

DOMAIN = "calculator"
PLATFORMS = ["number", "select", "sensor"]

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Calculator component."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Calculator from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Store calculator state
    hass.data[DOMAIN][entry.entry_id] = {
        "first_number": 0,
        "second_number": 0,
        "operation": "+",
        "result": 0
    }
    
    # Set up all platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok