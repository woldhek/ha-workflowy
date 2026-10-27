"""Config flow for Workflowy integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .api import WorkflowyApiClient
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class WorkflowyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Workflowy."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                client = WorkflowyApiClient(user_input["api_key"])
                await client.async_get_items()
                return self.async_create_entry(
                    title="Workflowy", data=user_input
                )
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception during Workflowy setup")
                errors["base"] = "cannot_connect"

        schema = vol.Schema(
            {
                vol.Required("api_key"): str,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return WorkflowyOptionsFlowHandler()


class WorkflowyOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Workflowy."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage options."""
        if user_input is not None:
            # Als de gebruiker meerdere opties selecteert (lijst), voeg ze samen tot komma-gescheiden waarden
            selected = user_input.get("parent_node_id", [])
            if isinstance(selected, list):
                user_input["parent_node_id"] = ", ".join(selected)
            return self.async_create_entry(title="", data=user_input)

        # Haal de client op om de beschikbare nodes uit te lezen
        client: WorkflowyApiClient = self.hass.data[DOMAIN][self.config_entry.entry_id]
        
        # Huidige selecties ophalen
        current_raw = self.config_entry.options.get(
            "parent_node_id", self.config_entry.data.get("parent_node_id", "")
        )
        current_selected = [n.strip() for n in current_raw.split(",") if n.strip()]

        # Nodes ophalen voor de keuzelijst
        node_options = [{"label": "Hoofdniveau (Root)", "value": ""}]
        try:
            items = await client.async_get_items()
            for item in items:
                node_id = item.get("id")
                node_name = item.get("name") or item.get("snippet") or node_id
                if node_id:
                    node_options.append({"label": node_name, "value": node_id})
        except Exception as err:
            _LOGGER.error("Fout bij het ophalen van Workflowy nodes voor opties: %s", err)

        options_schema = vol.Schema(
            {
                vol.Optional(
                    "parent_node_id",
                    default=current_selected,
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=node_options,
                        multiple=True,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(step_id="init", data_schema=options_schema)
