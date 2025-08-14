from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_LAKE_URL, CONF_LAKE_NAME, CONF_LAKE_ID
from .api import WassertemperaturClient


def _is_valid_domain(url: str) -> bool:
    try:
        p = urlparse(url)
        if p.scheme not in ("http", "https"):
            return False
        return p.netloc.endswith("wassertemperatur.org")
    except Exception:
        return False


class WassertemperaturConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            url = user_input.get(CONF_LAKE_URL, "").strip()
            if not _is_valid_domain(url):
                errors["base"] = "invalid_url"
            else:
                # Validate by fetching
                session = async_get_clientsession(self.hass)
                client = WassertemperaturClient(session)
                try:
                    data = await client.fetch_lake(url)
                except Exception:
                    errors["base"] = "cannot_connect"
                else:
                    # Proceed even if temperature is currently unavailable (e.g., "-°C")
                    unique_id = data.get("lake_id") or url
                    await self.async_set_unique_id(unique_id)
                    self._abort_if_unique_id_configured()
                    title = data.get("lake_name") or unique_id
                    return self.async_create_entry(
                        title=title,
                        data={
                            CONF_LAKE_URL: data["lake_url"],
                            CONF_LAKE_NAME: data["lake_name"],
                            CONF_LAKE_ID: data["lake_id"],
                        },
                    )

        data_schema = vol.Schema({vol.Required(CONF_LAKE_URL): str})
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)

    async def async_step_import(self, import_config: dict[str, Any]) -> FlowResult:
        # Not used, but kept for potential YAML import compatibility
        return await self.async_step_user(import_config)

    @staticmethod
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        return WassertemperaturOptionsFlow(config_entry)


class WassertemperaturOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, entry: config_entries.ConfigEntry) -> None:
        self._entry = entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            url = user_input.get(CONF_LAKE_URL, "").strip()
            if not _is_valid_domain(url):
                errors["base"] = "invalid_url"
            else:
                session = async_get_clientsession(self.hass)
                client = WassertemperaturClient(session)
                try:
                    data = await client.fetch_lake(url)
                except Exception:
                    errors["base"] = "cannot_connect"
                else:
                    # Allow URL change even if current temperature is unavailable
                    return self.async_create_entry(title="", data={CONF_LAKE_URL: url})

        default = self._entry.data.get(CONF_LAKE_URL) or self._entry.options.get(CONF_LAKE_URL) or ""
        schema = vol.Schema({vol.Required(CONF_LAKE_URL, default=default): str})
        return self.async_show_form(step_id="init", data_schema=schema, errors=errors)
