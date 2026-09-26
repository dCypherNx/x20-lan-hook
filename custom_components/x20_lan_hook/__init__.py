from __future__ import annotations

import importlib
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import (
    CONF_DEBUG_CAPTURE,
    CONF_DEVICE_DID,
    DATA_RUNTIME,
    DOMAIN,
    PLATFORMS,
    SIGNAL_UPDATE,
)
from .decoder import ingest
from .runtime import X20Runtime

_LOGGER = logging.getLogger(__name__)

_PATCHED = False
_ORIGINAL_HANDLER = None


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    runtime = X20Runtime(
        device_did=entry.data.get(CONF_DEVICE_DID) or None,
        debug_capture=bool(entry.data.get(CONF_DEBUG_CAPTURE, False)),
    )
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {DATA_RUNTIME: runtime}

    _install_hook(hass)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return unloaded


def _install_hook(hass: HomeAssistant) -> None:
    global _PATCHED, _ORIGINAL_HANDLER

    if _PATCHED:
        return

    try:
        miot_lan_mod = importlib.import_module(
            "custom_components.xiaomi_home.miot.miot_lan"
        )
    except Exception as exc:
        _LOGGER.error("Failed to import Xiaomi Home MIoT LAN module: %s", exc)
        return

    miot_lan_class = getattr(miot_lan_mod, "MIoTLan", None)
    if miot_lan_class is None:
        _LOGGER.error("MIoTLan class not found")
        return

    original = getattr(miot_lan_class, "_MIoTLan__message_handler", None)
    if original is None:
        _LOGGER.error("MIoTLan.__message_handler not found")
        return

    _ORIGINAL_HANDLER = original

    def wrapped(self, did: str, msg: dict[str, Any]) -> Any:
        result = original(self, did, msg)

        try:
            if msg.get("method") != "properties_changed":
                return result

            entries = hass.data.get(DOMAIN, {})
            if not entries:
                return result

            changed = False
            for prop in msg.get("params", []):
                siid = prop.get("siid")
                piid = prop.get("piid")
                if not isinstance(siid, int) or not isinstance(piid, int):
                    continue

                value = prop.get("value")
                for entry_data in entries.values():
                    runtime: X20Runtime = entry_data[DATA_RUNTIME]
                    if not runtime.accepts(did):
                        continue

                    ingest(runtime, siid, piid, value)
                    changed = True

                    if runtime.debug_capture:
                        _LOGGER.debug(
                            "X20 LAN did=%s siid=%s piid=%s value=%r",
                            did,
                            siid,
                            piid,
                            value,
                        )

            if changed:
                hass.add_job(async_dispatcher_send, hass, SIGNAL_UPDATE)
        except Exception:
            _LOGGER.exception("Error while processing Xiaomi Home LAN payload")

        return result

    setattr(miot_lan_class, "_MIoTLan__message_handler", wrapped)
    _PATCHED = True
    _LOGGER.info("X20 LAN Hook installed on MIoTLan.__message_handler")
