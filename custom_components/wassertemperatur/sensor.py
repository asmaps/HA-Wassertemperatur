from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_LAKE_NAME, CONF_LAKE_URL, CONF_LAKE_ID


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    async_add_entities([WassertemperaturSensor(coordinator, entry)])


class WassertemperaturSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = False
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = "°C"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        # Stable unique id per config entry to support changing lakes via options
        self._attr_unique_id = entry.entry_id

    @property
    def name(self) -> str | None:
        lake_name = None
        if self.coordinator.data:
            lake_name = self.coordinator.data.get("lake_name")
        return lake_name or "Water Temperature"

    @property
    def device_info(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        lake_id = data.get("lake_id") or self._entry.data.get(CONF_LAKE_ID)
        lake_name = data.get("lake_name") or self._entry.data.get(CONF_LAKE_NAME)
        lake_url = data.get("lake_url") or self._entry.data.get(CONF_LAKE_URL)
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": lake_name or lake_id or "Wassertemperatur",
            "manufacturer": "wassertemperatur.org",
            "model": "Lake Water Temperature",
            "configuration_url": lake_url,
        }

    @property
    def native_value(self) -> float | None:
        temp = self.coordinator.data.get("temperature_c") if self.coordinator.data else None
        return temp

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        data = self.coordinator.data or {}
        return {
            "lake_id": data.get("lake_id") or self._entry.data.get(CONF_LAKE_ID),
            "lake_name": data.get("lake_name") or self._entry.data.get(CONF_LAKE_NAME),
            "lake_url": data.get("lake_url") or self._entry.data.get(CONF_LAKE_URL),
            "attribution": "Data provided by wassertemperatur.org",
        }
