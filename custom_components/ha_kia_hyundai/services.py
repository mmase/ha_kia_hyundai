from logging import getLogger
from typing import cast

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_DEVICE_ID
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers import device_registry

from .const import DOMAIN, STR_TO_ENUM
from .vehicle_coordinator import VehicleCoordinator

SERVICE_START_CLIMATE = "start_climate"
SERVICE_SET_CHARGE_LIMIT = "set_charge_limits"

SERVICE_ATTRIBUTE_CLIMATE = "climate"
SERVICE_ATTRIBUTE_TEMPERATURE = "temperature"
SERVICE_ATTRIBUTE_DEFROST = "defrost"
SERVICE_ATTRIBUTE_HEATING = "heating"
SERVICE_ATTRIBUTE_DRIVER_SEAT = "driver_seat"
SERVICE_ATTRIBUTE_PASSENGER_SEAT = "passenger_seat"
SERVICE_ATTRIBUTE_LEFT_REAR_SEAT = "left_rear_seat"
SERVICE_ATTRIBUTE_RIGHT_REAR_SEAT = "right_rear_seat"

SUPPORTED_SERVICES = (
    SERVICE_START_CLIMATE,
    SERVICE_SET_CHARGE_LIMIT,
)

_LOGGER = getLogger(__name__)


def async_setup_services(hass: HomeAssistant):
    async def async_handle_start_climate(call: ServiceCall):
        coordinator: VehicleCoordinator = _get_coordinator_from_device(hass, call)
        climate = call.data.get(SERVICE_ATTRIBUTE_CLIMATE)
        set_temp = call.data.get(SERVICE_ATTRIBUTE_TEMPERATURE)
        defrost = call.data.get(SERVICE_ATTRIBUTE_DEFROST)
        heating = call.data.get(SERVICE_ATTRIBUTE_HEATING)
        driver_seat = call.data.get(SERVICE_ATTRIBUTE_DRIVER_SEAT, None)
        passenger_seat = call.data.get(SERVICE_ATTRIBUTE_PASSENGER_SEAT, None)
        left_rear_seat = call.data.get(SERVICE_ATTRIBUTE_LEFT_REAR_SEAT, None)
        right_rear_seat = call.data.get(SERVICE_ATTRIBUTE_RIGHT_REAR_SEAT, None)

        if set_temp is not None:
            set_temp = int(set_temp)
        if driver_seat is not None:
            driver_seat = STR_TO_ENUM[driver_seat]
        if passenger_seat is not None:
            passenger_seat = STR_TO_ENUM[passenger_seat]
        if left_rear_seat is not None:
            left_rear_seat = STR_TO_ENUM[left_rear_seat]
        if right_rear_seat is not None:
            right_rear_seat = STR_TO_ENUM[right_rear_seat]

        # Use the vehicle manager to start climate
        await hass.async_add_executor_job(
            coordinator.vehicle_manager.start_climate,
            coordinator.vehicle_id,
            set_temp,
            defrost,
            climate,
            heating,
        )
        
        coordinator.async_update_listeners()
        await coordinator.async_request_refresh()

    async def async_handle_set_charge_limit(call: ServiceCall):
        coordinator: VehicleCoordinator = _get_coordinator_from_device(hass, call)
        ac_limit = int(call.data.get("ac_limit"))
        dc_limit = int(call.data.get("dc_limit"))

        # Use the vehicle manager to set charge limits
        await hass.async_add_executor_job(
            coordinator.vehicle_manager.set_charge_limits,
            coordinator.vehicle_id,
            ac_limit,
            dc_limit,
        )
        
        coordinator.async_update_listeners()
        await coordinator.async_request_refresh()

    services = {
        SERVICE_START_CLIMATE: async_handle_start_climate,
        SERVICE_SET_CHARGE_LIMIT: async_handle_set_charge_limit,
    }
    for service in SUPPORTED_SERVICES:
        hass.services.async_register(DOMAIN, service, services[service])

    return True


def _get_coordinator_from_device(
        hass: HomeAssistant, call: ServiceCall
) -> VehicleCoordinator:
    """Get coordinator from device ID."""
    # Get all entry data
    entry_datas = list(hass.data[DOMAIN].values())
    
    # If only one account, get coordinators from it
    if len(entry_datas) == 1:
        coordinators = entry_datas[0]["coordinators"]
        # Return first coordinator if only one vehicle
        if len(coordinators) == 1:
            return next(iter(coordinators.values()))
    
    # Multiple vehicles/accounts - need to find the right one
    device_entry = device_registry.async_get(hass).async_get(
        call.data[ATTR_DEVICE_ID]
    )
    
    if not device_entry:
        raise ValueError("Device not found")
    
    config_entry_ids = device_entry.config_entries
    config_entry_id = next(
        (
            config_entry_id
            for config_entry_id in config_entry_ids
            if cast(
                ConfigEntry,
                hass.config_entries.async_get_entry(config_entry_id),
            ).domain == DOMAIN
        ),
        None,
    )
    
    if not config_entry_id:
        raise ValueError("Config entry not found")
    
    entry_data = hass.data[DOMAIN][config_entry_id]
    coordinators = entry_data["coordinators"]
    
    # Find the coordinator for this device
    # Match by vehicle name in device identifiers
    for vehicle_id, coordinator in coordinators.items():
        if coordinator.vehicle_name in str(device_entry.identifiers):
            return coordinator
    
    # Fallback: return first coordinator
    return next(iter(coordinators.values()))


@callback
def async_unload_services(hass) -> None:
    for service in SUPPORTED_SERVICES:
        hass.services.async_remove(DOMAIN, service)
