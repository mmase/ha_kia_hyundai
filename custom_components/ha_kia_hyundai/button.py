from logging import getLogger

from homeassistant.components.button import ButtonEntity, ButtonDeviceClass, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import VehicleCoordinator
from .const import DOMAIN
from .vehicle_coordinator_base_entity import VehicleCoordinatorBaseEntity

_LOGGER = getLogger(__name__)
PARALLEL_UPDATES: int = 1


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    """Set up button entities."""
    entry_data = hass.data[DOMAIN][config_entry.entry_id]
    coordinators = entry_data["coordinators"]
    
    buttons = []
    for coordinator in coordinators.values():
        buttons.append(RequestUpdateFromCarButton(coordinator=coordinator))
    
    if buttons:
        async_add_entities(buttons)


class RequestUpdateFromCarButton(VehicleCoordinatorBaseEntity, ButtonEntity):
    def __init__(
            self,
            coordinator: VehicleCoordinator,
    ):
        super().__init__(coordinator, ButtonEntityDescription(
            key="request_vehicle_data_sync",
            name="Request Wake Up from Car (hurts 12v battery)",
            device_class=ButtonDeviceClass.UPDATE,
        ))

    async def async_press(self) -> None:
        """Press the button."""
        await self.hass.async_add_executor_job(
            self.coordinator.vehicle_manager.force_refresh_vehicle_state,
            self.coordinator.vehicle_id
        )
        self.coordinator.async_update_listeners()
        await self.coordinator.async_request_refresh()
