import logging 
from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)


NUMBER_ENTITIES = [
    NumberEntityDescription(
        key="first_number",
        name="First Number",
        min_value=-1000,
        max_value=1000,
        step=1,
        unit_of_measurement="units",
    ),
    NumberEntityDescription(
        key="second_number",
        name="Second Number",
        min_value=-1000,
        max_value=1000,
        step=1,
        unit_of_measurement="units",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    calculator_data = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for description in NUMBER_ENTITIES:
        entities.append(
            CalculatorNumber(
                hass=hass,
                entry_id=entry.entry_id,
                description=description,
                calculator_data=calculator_data,
            )
        )

    async_add_entities(entities)


class CalculatorNumber(NumberEntity, RestoreEntity):
    """Representation of a Calculator Number entity."""

    def __init__(self, hass, config_entry, description, calculator_data):
        """Initialize the number."""
        self.hass = hass
        self._config_entry = config_entry
        self.entity_description = description
        self._calculator_data = calculator_data
        self._attr_unique_id = f"{config_entry.entry_id}_{description.key}"
        self._attr_name = f"{description.name}"
        self._attr_native_min_value = -1000
        self._attr_native_max_value = 1000
        self._attr_native_step = 1
        self._attr_native_value = 0


    @property
    def native_value(self) -> float | None:
        return self._calculator_data.get(self.entity_description.key, 0)
    
    async def async_set_native_value(self, value: float) -> None:   
        self._calculate_data[self.entity_description.key] = value
        await self._calculate_result()
        await self._update_sensor_entity()
    
    async def _calculate_result(self):
        first = self._calculator_data.get('first_number', 0)
        second = self._calculator_data.get('second_number', 0)
        operation = self._calculator_data.get('operation', '+')

        try:
            if operation == "+":
                result = first + second
            elif operation == "-":
                result = first - second
            elif operation == "×":
                result = first * second
            elif operation == "÷":
                if second == 0:
                    result = "Error: Division by zero"
                else:
                    result = first / second
            else:
                result = 0
                
            self._calculator_data["result"] = result
        except Exception as e:
            self._calculator_data["result"] = f"Error: {str(e)}"
    
    async def _update_sensor_entity(self):
        sensor_entities = [
            entity for entity in self.hass.data[DOMAIN].values() 
            if hasattr(entity, 'entity_id') and 'sensor' in entity.entity_id
        ]
        
        for sensor in sensor_entities:
            sensor.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        
        if (last_state := await self.async_get_last_state()) is not None:
            if last_state.state not in (None, "unknown", "unavailable"):
                self._calculator_data[self.entity_description.key] = float(last_state.state)
    
