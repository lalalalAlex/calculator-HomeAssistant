import logging
from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

SELECT_DESCRIPTION = SelectEntityDescription(
    key="operation",
    name="Operation",
    options=["+", "-", "×", "÷"],
)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    calculator_data = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([
        CalculatorSelect(
            hass=hass,
            config_entry=config_entry,
            description=SELECT_DESCRIPTION,
            calculator_data=calculator_data
        )
    ])

class CalculatorSelect(SelectEntity, RestoreEntity):
    def __init__(self, hass, config_entry, description, calculator_data):
        self.hass = hass
        self._config_entry = config_entry
        self.entity_description = description
        self._calculator_data = calculator_data
        self._attr_unique_id = f"{config_entry.entry_id}_{description.key}"
        self._attr_current_option = "+"

    @property
    def current_option(self) -> str:
        return self._calculator_data.get("operation", "+")

    async def async_select_option(self, option: str) -> None:
        if option not in self.entity_description.options:
            raise ValueError(f"Operation {option} is not valid")
        
        self._calculator_data["operation"] = option
        self._attr_current_option = option
        
        await self._calculate_result()
        
        # Write state
        self.async_write_ha_state()
        
        await self._update_number_entities()

    async def _calculate_result(self):
        first = self._calculator_data.get("first_number", 0)
        second = self._calculator_data.get("second_number", 0)
        operation = self._calculator_data.get("operation", "+")
        
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

    async def _update_number_entities(self):
        for entity in self.hass.data[DOMAIN].values():
            if hasattr(entity, 'async_write_ha_state'):
                entity.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        """Run when entity is added to hass."""
        await super().async_added_to_hass()
        
        if (last_state := await self.async_get_last_state()) is not None:
            if last_state.state in self.entity_description.options:
                self._calculator_data["operation"] = last_state.state
                self._attr_current_option = last_state.state