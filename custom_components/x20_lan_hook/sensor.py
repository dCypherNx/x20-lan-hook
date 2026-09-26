from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DATA_RUNTIME, DOMAIN, SIGNAL_UPDATE
from .runtime import X20Runtime


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    runtime: X20Runtime = hass.data[DOMAIN][entry.entry_id][DATA_RUNTIME]
    async_add_entities(
        [
            X20MapSensor(runtime, entry),
            X20RoomSensor(runtime, entry),
            X20PropertySensor(runtime, entry),
        ]
    )


class X20BaseSensor(SensorEntity):
    _attr_should_poll = False

    def __init__(self, runtime: X20Runtime, entry: ConfigEntry) -> None:
        self._runtime = runtime
        self._entry = entry

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(self.hass, SIGNAL_UPDATE, self._handle_update)
        )

    @callback
    def _handle_update(self) -> None:
        self.async_write_ha_state()


class X20MapSensor(X20BaseSensor):
    _attr_name = "X20 current map"
    _attr_icon = "mdi:map"

    def __init__(self, runtime: X20Runtime, entry: ConfigEntry) -> None:
        super().__init__(runtime, entry)
        self._attr_unique_id = f"{entry.entry_id}_current_map"

    @property
    def native_value(self) -> str | int | None:
        return self._runtime.current_map_name or self._runtime.current_map_id

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "map_id": self._runtime.current_map_id,
            "map_name": self._runtime.current_map_name,
            "rooms": self._runtime.rooms,
        }


class X20RoomSensor(X20BaseSensor):
    _attr_name = "X20 current room"
    _attr_icon = "mdi:floor-plan"

    def __init__(self, runtime: X20Runtime, entry: ConfigEntry) -> None:
        super().__init__(runtime, entry)
        self._attr_unique_id = f"{entry.entry_id}_current_room"

    @property
    def native_value(self) -> str | int | None:
        return self._runtime.current_room_name or self._runtime.current_room_id

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "room_id": self._runtime.current_room_id,
            "room_name": self._runtime.current_room_name,
            "map_id": self._runtime.current_map_id,
        }


class X20PropertySensor(X20BaseSensor):
    _attr_name = "X20 MIoT properties"
    _attr_icon = "mdi:lan"

    def __init__(self, runtime: X20Runtime, entry: ConfigEntry) -> None:
        super().__init__(runtime, entry)
        self._attr_unique_id = f"{entry.entry_id}_miot_properties"

    @property
    def native_value(self) -> int:
        return len(self._runtime.properties)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            f"{siid}.{piid}": prop.value
            for (siid, piid), prop in sorted(self._runtime.properties.items())
        }
