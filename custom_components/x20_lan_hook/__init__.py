from __future__ import annotations

import logging
import importlib
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)

DOMAIN = "x20_lan_hook"


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    try:
        miot_lan_mod = importlib.import_module(
            "custom_components.xiaomi_home.miot.miot_lan"
        )
    except Exception as exc:
        _LOGGER.error("x20_lan_hook: falha ao importar miot_lan: %s", exc)
        return True

    MiotLanClass = getattr(miot_lan_mod, "MIoTLan", None)
    if MiotLanClass is None:
        _LOGGER.error("x20_lan_hook: classe MIoTLan não encontrada")
        return True

    # método "privado" name-mangled
    original = getattr(MiotLanClass, "_MIoTLan__message_handler", None)
    if original is None:
        _LOGGER.error(
            "x20_lan_hook: método __message_handler não encontrado em MIoTLan"
        )
        return True

    def wrapped(self, did: str, msg: dict) -> None:
        # chama o handler original primeiro
        result = original(self, did, msg)

        try:
            if msg.get("method") == "properties_changed":
                for p in msg.get("params", []):
                    siid = p.get("siid")
                    piid = p.get("piid")
                    value = p.get("value")

                    # queremos todos os dids, mas só o par (siid=2, piid=2)
                    if siid == 2 and piid == 2:
                        entity_id = f"sensor.xiaomi_{did}_p_2_2"

                        _LOGGER.debug(
                            "x20_lan_hook: atualizando %s = %s (siid=%s, piid=%s, did=%s)",
                            entity_id,
                            value,
                            siid,
                            piid,
                            did,
                        )

                        hass.add_job(
                            hass.states.async_set,
                            entity_id,
                            value,
                            {
                                "friendly_name": f"Xiaomi {did} MIoT status",
                                "siid": siid,
                                "piid": piid,
                                "did": did,
                            },
                        )
        except Exception as exc:
            _LOGGER.warning("x20_lan_hook: erro ao processar msg: %s", exc)

        return result

    setattr(MiotLanClass, "_MIoTLan__message_handler", wrapped)
    _LOGGER.info("x20_lan_hook: hook aplicado em MIoTLan.__message_handler")
    return True
