import logging
import time
import uuid
from datetime import datetime, timedelta, timezone

from homeassistant.core import HomeAssistant
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_SCAN_INTERVAL,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from kia_hyundai_api import UsKia, AuthError

from .const import (
    CONF_ACCESS_TOKEN,
    CONF_DEVICE_ID,
    CONF_REFRESH_TOKEN,
    DOMAIN,
    PLATFORMS,
    CONF_VEHICLE_ID,
    DEFAULT_SCAN_INTERVAL,
    CONFIG_FLOW_VERSION,
)
from .services import async_setup_services, async_unload_services
from .vehicle_coordinator import VehicleCoordinator


_LOGGER = logging.getLogger(__name__)


def _get_patched_api_headers(api_instance, vehicle_key: str | None = None) -> dict:
    """Generate working headers for Kia USA API with updated app version and secrets.
    
    The kia-hyundai-api library uses outdated headers that no longer work with
    the Kia USA API. This function provides the correct iOS headers that work.
    """
    offset = time.localtime().tm_gmtoff / 60 / 60
    client_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, api_instance.device_id)
    
    headers = {
        "content-type": "application/json;charset=utf-8",
        "accept": "application/json",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "accept-charset": "utf-8",
        "apptype": "L",
        "appversion": "7.22.0",
        "clientid": "SPACL716-APL",
        "clientuuid": str(client_uuid),
        "from": "SPA",
        "host": "api.owners.kia.com",
        "language": "0",
        "offset": str(int(offset)),
        "ostype": "iOS",
        "osversion": "15.8.5",
        "phonebrand": "iPhone",
        "secretkey": "sydnat-9kykci-Kuhtep-h5nK",
        "to": "APIGW",
        "tokentype": "A",
        "user-agent": "KIAPrimo_iOS/37 CFNetwork/1335.0.3.4 Darwin/21.6.0",
        "date": datetime.now(tz=timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT"),
        "deviceid": api_instance.device_id,
    }
    
    # Add dynamic headers from the original method
    if api_instance.session_id is not None:
        headers["sid"] = api_instance.session_id
    if api_instance.refresh_token is not None:
        headers["rmtoken"] = api_instance.refresh_token
    if api_instance.otp_key is not None:
        headers["otpkey"] = api_instance.otp_key
        if api_instance.notify_type is not None:
            headers["notifytype"] = api_instance.notify_type
        if api_instance.last_action is not None and "xid" in api_instance.last_action:
            headers["xid"] = api_instance.last_action["xid"]
    if vehicle_key is not None:
        headers["vinkey"] = vehicle_key
    return headers


def patch_api_headers(api_connection: UsKia) -> None:
    """Monkeypatch the API headers on a UsKia instance."""
    _LOGGER.debug("Patching Kia USA API headers with updated iOS headers")
    api_connection._api_headers = lambda vehicle_key=None: _get_patched_api_headers(api_connection, vehicle_key)


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Migrate old entry."""
    _LOGGER.debug("Migrating configuration from version %s.%s", config_entry.version, config_entry.minor_version)

    if config_entry.version > CONFIG_FLOW_VERSION:
        # This means the user has downgraded from a future version
        return False

    if config_entry.version == 2:
        _LOGGER.debug(f"old config data:{config_entry.data}")
        new_data = {
            CONF_USERNAME: config_entry.data[CONF_USERNAME],
            CONF_PASSWORD: config_entry.data[CONF_PASSWORD],
            CONF_VEHICLE_ID: config_entry.data["vehicle_identifier"],
        }
        hass.config_entries.async_update_entry(config_entry, data=new_data, minor_version=1, version=CONFIG_FLOW_VERSION)

    _LOGGER.debug("Migration to configuration version %s.%s successful", config_entry.version, config_entry.minor_version)

    return True

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    hass.data.setdefault(DOMAIN, {})
    async_setup_services(hass)

    vehicle_id = config_entry.data[CONF_VEHICLE_ID]
    username = config_entry.data[CONF_USERNAME]
    password = config_entry.data[CONF_PASSWORD]
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    refresh_token = config_entry.data.get(CONF_REFRESH_TOKEN)

    scan_interval = timedelta(
        minutes=config_entry.options.get(
            CONF_SCAN_INTERVAL,
            DEFAULT_SCAN_INTERVAL,
        )
    )

    client_session = async_get_clientsession(hass)
    async def otp_callback(context: dict[str, str]):
        raise ConfigEntryAuthFailed("otp required")
    api_connection = UsKia(
        username=username,
        password=password,
        client_session=client_session,
        otp_callback=otp_callback,
        device_id=device_id,
        refresh_token=refresh_token,
    )
    
    # Monkeypatch the API headers with working iOS headers
    patch_api_headers(api_connection)
    
    try:
        await api_connection.get_vehicles()
    except AuthError as err:
        raise ConfigEntryAuthFailed(err) from err
    coordinator: VehicleCoordinator | None = None
    if api_connection.vehicles is None:
        raise ConfigEntryError("no vehicles found")
    for vehicle in api_connection.vehicles:
        if vehicle_id == vehicle["vehicleIdentifier"]:
            coordinator = VehicleCoordinator(
                hass=hass,
                config_entry=config_entry,
                vehicle_id=vehicle["vehicleIdentifier"],
                vehicle_name=vehicle["nickName"],
                vehicle_model=vehicle["modelName"],
                api_connection=api_connection,
                scan_interval=scan_interval,
            )
    if coordinator is None:
        raise ConfigEntryError("vehicle not found")
    _LOGGER.debug("first update start")
    await coordinator.async_config_entry_first_refresh()
    _LOGGER.debug("first update finished")

    hass.data[DOMAIN][vehicle_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    if not config_entry.update_listeners:
        config_entry.add_update_listener(async_update_options)

    return True

async def async_update_options(hass: HomeAssistant, config_entry: ConfigEntry):
    await hass.config_entries.async_reload(config_entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    if unload_ok :=  await hass.config_entries.async_unload_platforms(
        config_entry, PLATFORMS
    ):
        vehicle_id = config_entry.unique_id
        await hass.data[DOMAIN][vehicle_id].api_connection.api_session.close()
        del hass.data[DOMAIN][vehicle_id]
    if not hass.data[DOMAIN]:
        async_unload_services(hass)
    return unload_ok
