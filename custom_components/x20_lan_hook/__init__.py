from __future__ import annotations

import importlib
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)

DOMAIN = "x20_lan_hook"
CONF_CAPTURE_PROPERTIES = "capture_properties"
CONF_CAPTURE_DID = "capture_did"


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    domain_config = config.get(DOMAIN) or {}
    capture_properties = bool(domain_config.get(CONF_CAPTURE_PROPERTIES, False))
    capture_did = domain_config.get(CONF_CAPTURE_DID)

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

    def wrapped(self, did: str, msg: dict[str, Any]) -> None:
        # chama o handler original primeiro
        result = original(self, did, msg)

        try:
            if msg.get("method") != "properties_changed":
                return result

            for p in msg.get("params", []):
                siid = p.get("siid")
                piid = p.get("piid")
                value = p.get("value")

                # Diagnóstico temporário para descobrir propriedades que mudam
                # durante deslocamento/limpeza. Não cria entidades adicionais.
                if capture_properties and (
                    capture_did is None or str(did) == str(capture_did)
                ):
                    _LOGGER.warning(
                        "X20_CAPTURE did=%s siid=%s piid=%s value=%r",
                        did,
                        siid,
                        piid,
                        value,
                    )

                # comportamento original: preservar o status bruto 2/2
                if siid == 2 and piid == 2:
                    entity_id = f"sensor.xiaomi_{did}_p_2_2"

                    _LOGGER.debug(
                        "x20_lan_hook: atualizando %s = %s "
                        "(siid=%s, piid=%s, did=%s)",
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
    _LOGGER.info(
        "x20_lan_hook: hook aplicado em MIoTLan.__message_handler "
        "(capture_properties=%s, capture_did=%s)",
        capture_properties,
        capture_did or "todos",
    )
    return True
