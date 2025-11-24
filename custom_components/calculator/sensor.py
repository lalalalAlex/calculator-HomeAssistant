import logging
from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

SENSOR_DESCRIPTION = SensorEntityDescription(
    key="calculator_result",
    name="Calculator Result",
)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    calculator_data = hass.data[DOMAIN][config_entry.entry_id]
    
    sensor_entity = CalculatorSensor(
        hass=hass,
        config_entry=config_entry,
        description=SENSOR_DESCRIPTION,
        calculator_data=calculator_data
    )
    
    hass.data[DOMAIN]["sensor_entity"] = sensor_entity
    async_add_entities([sensor_entity])

class CalculatorSensor(SensorEntity, RestoreEntity):
    """Representation of a Calculator Result Sensor."""

    def __init__(self, hass, config_entry, description, calculator_data):
        """Initialize the sensor."""
        self.hass = hass
        self._config_entry = config_entry
        self.entity_description = description
        self._calculator_data = calculator_data
        self._attr_unique_id = f"{config_entry.entry_id}_{description.key}"
        self._attr_native_value = 0

    @property
    def native_value(self):
        result = self._calculator_data.get("result", 0)
        if isinstance(result, str):
            return result
        return float(result) if result is not None else 0

    @property
    def extra_state_attributes(self):
        return {
            "first_number": self._calculator_data.get("first_number", 0),
            "second_number": self._calculator_data.get("second_number", 0),
            "operation": self._calculator_data.get("operation", "+"),
            "calculation": self._get_calculation_string()
        }

    def _get_calculation_string(self) -> str:
        first = self._calculator_data.get("first_number", 0)
        second = self._calculator_data.get("second_number", 0)
        operation = self._calculator_data.get("operation", "+")
        return f"{first} {operation} {second}"

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        
        if (last_state := await self.async_get_last_state()) is not None:
            if last_state.state not in (None, "unknown", "unavailable"):
                try:
                    self._calculator_data["result"] = float(last_state.state)
                except (ValueError, TypeError):
                    self._calculator_data["result"] = last_state.state