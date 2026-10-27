"""Support for Workflowy sensor platform."""
from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import WorkflowyApiClient
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=5)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Workflowy sensor platform."""
    client: WorkflowyApiClient = hass.data[DOMAIN][entry.entry_id]
    
    raw_node_ids = entry.options.get(
        "parent_node_id", entry.data.get("parent_node_id", "")
    )
    
    node_ids = [node.strip() for node in raw_node_ids.split(",") if node.strip()]
    if not node_ids:
        node_ids = [""]

    entities = []
    for node_id in node_ids:
        entities.append(WorkflowyRootNodeSensor(client, entry.title, node_id))

    async_add_entities(entities, update_before_add=True)


class WorkflowyRootNodeSensor(SensorEntity):
    """Sensor showing the Workflowy Root/Parent Node Item Count."""

    _attr_icon = "mdi:format-list-bulleted-type"
    _attr_native_unit_of_measurement = "items"

    def __init__(
        self,
        client: WorkflowyApiClient,
        entry_title: str,
        parent_node_id: str = "",
    ) -> None:
        """Initialize the sensor."""
        self._client = client
        self._parent_node_id = parent_node_id
        self._entry_title = entry_title
        
        # Initiële naam (wordt bij update vervangen door de echte node naam)
        suffix = f" ({parent_node_id})" if parent_node_id else ""
        self._attr_name = f"{entry_title}{suffix}"
        self._attr_unique_id = f"workflowy_root_node_{parent_node_id or 'default'}"
        self._attr_native_value = None

    async def async_update(self) -> None:
        """Fetch node name and item count from Workflowy API."""
        try:
            # 1. Haal de onderliggende items op voor de waarde (item count)
            items = await self._client.async_get_items(self._parent_node_id)
            self._attr_native_value = len(items)

            # 2. Haal de exacte naam van de parent node op voor self._attr_name
            node_name = None
            if self._parent_node_id:
                if hasattr(self._client, "async_get_node"):
                    node_data = await self._client.async_get_node(self._parent_node_id)
                    if node_data and isinstance(node_data, dict):
                        node_info = node_data.get("node", node_data)
                        node_name = node_info.get("name") or node_info.get("snippet")

                if not node_name:
                    all_nodes = await self._client.async_get_items()
                    for node in all_nodes:
                        if node.get("id") == self._parent_node_id:
                            node_name = node.get("name") or node.get("snippet")
                            break

            if node_name:
                self._attr_name = node_name
            else:
                self._attr_name = "Workflowy Root"

        except Exception as err:
            _LOGGER.error("Fout bij het ophalen van de Workflowy sensor data: %s", err)
            self._attr_native_value = None
