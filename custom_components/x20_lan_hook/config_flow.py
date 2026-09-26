from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_DEBUG_CAPTURE, CONF_DEVICE_DID, DOMAIN


class X20LanHookConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        if user_input is not None:
            did = user_input.get(CONF_DEVICE_DID, "").strip()
            await self.async_set_unique_id(did or DOMAIN)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title="X20 LAN Hook",
                data={
                    CONF_DEVICE_DID: did,
                    CONF_DEBUG_CAPTURE: user_input.get(CONF_DEBUG_CAPTURE, False),
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_DEVICE_DID, default=""): str,
                    vol.Optional(CONF_DEBUG_CAPTURE, default=False): bool,
                }
            ),
        )
