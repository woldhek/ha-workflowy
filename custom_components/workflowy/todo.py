"""Support for Workflowy To-Do lists."""
from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.components.todo import (
    TodoItem,
    TodoItemStatus,
    TodoListEntity,
    TodoListEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import WorkflowyApiClient
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=30)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Workflowy todo platform."""
    client: WorkflowyApiClient = hass.data[DOMAIN][entry.entry_id]
    
    raw_node_ids = entry.options.get(
        "parent_node_id", entry.data.get("parent_node_id", "")
    )
    
    node_ids = [node.strip() for node in raw_node_ids.split(",") if node.strip()]
    if not node_ids:
        node_ids = [""]

    entities = []
    for node_id in node_ids:
        entities.append(WorkflowyTodoListEntity(client, entry.title, node_id))

    async_add_entities(entities, update_before_add=True)


class WorkflowyTodoListEntity(TodoListEntity):
    """Workflowy Todo List Entity."""

    _attr_supported_features = (
        TodoListEntityFeature.CREATE_TODO_ITEM
        | TodoListEntityFeature.UPDATE_TODO_ITEM
        | TodoListEntityFeature.DELETE_TODO_ITEM
        | TodoListEntityFeature.SET_DESCRIPTION_ON_ITEM
    )

    def __init__(
        self,
        client: WorkflowyApiClient,
        entry_title: str,
        parent_node_id: str = "",
    ) -> None:
        """Initialize the todo list."""
        self._client = client
        self._parent_node_id = parent_node_id
        self._entry_title = entry_title
        
        suffix = f" ({parent_node_id})" if parent_node_id else ""
        self._attr_name = f"{entry_title}{suffix}"
        self._attr_unique_id = f"workflowy_todo_{parent_node_id or 'root'}"
        self._items: list[TodoItem] = []

    @property
    def todo_items(self) -> list[TodoItem] | None:
        """Return the todo items."""
        return self._items

    async def async_update(self) -> None:
        """Update the todo list and list name from Workflowy."""
        if self._parent_node_id:
            try:
                if hasattr(self._client, "async_get_node"):
                    node_data = await self._client.async_get_node(self._parent_node_id)
                    if node_data and isinstance(node_data, dict):
                        node_info = node_data.get("node", node_data)
                        name = node_info.get("name") or node_info.get("snippet")
                        if name:
                            self._attr_name = name

                if self._attr_name == f"{self._entry_title} ({self._parent_node_id})":
                    all_nodes = await self._client.async_get_items()
                    for node in all_nodes:
                        if node.get("id") == self._parent_node_id:
                            name = node.get("name") or node.get("snippet")
                            if name:
                                self._attr_name = name
                                break
            except Exception as err:
                _LOGGER.debug("Could not fetch name for parent node %s: %s", self._parent_node_id, err)
        else:
            self._attr_name = "Workflowy Root"

        nodes = await self._client.async_get_items(self._parent_node_id)
        items = []
        for node in nodes:
            status = (
                TodoItemStatus.COMPLETED
                if node.get("completed_at") or node.get("completed")
                else TodoItemStatus.NEEDS_ACTION
            )
            items.append(
                TodoItem(
                    summary=node.get("name", ""),
                    uid=node.get("id"),
                    status=status,
                    description=node.get("note", "") or "",
                )
            )
        self._items = items

    async def async_create_todo_item(self, item: TodoItem) -> None:
        """Create a new todo item in Workflowy with description/note."""
        response = await self._client.async_create_item(
            summary=item.summary,
            note=item.description,
            parent_node_id=self._parent_node_id,
        )

        if self.hass:
            self.hass.bus.async_fire(
                "workflowy_todo_item_created",
                {
                    "entity_id": self.entity_id,
                    "summary": item.summary,
                    "description": item.description,
                    "item_id": response.get("id") if isinstance(response, dict) else None,
                    "parent_node_id": self._parent_node_id,
                },
            )

        await self.async_update()
        self.async_write_ha_state()

    async def async_update_todo_item(self, item: TodoItem) -> None:
        """Update a todo item in Workflowy including description/note."""
        completed = item.status == TodoItemStatus.COMPLETED
        # Garandeer dat description als string wordt meegegeven
        note_text = item.description if item.description is not None else ""
        
        await self._client.async_update_item(
            item_id=item.uid,
            summary=item.summary,
            note=note_text,
            completed=completed,
        )

        # Werk de lokale cache direct bij
        for existing_item in self._items:
            if existing_item.uid == item.uid:
                existing_item.summary = item.summary
                existing_item.status = item.status
                existing_item.description = note_text
                break

        self.async_write_ha_state()

    async def async_delete_todo_items(self, uids: list[str]) -> None:
        """Delete todo items in Workflowy."""
        for uid in uids:
            await self._client.async_delete_item(uid)
        await self.async_update()
        self.async_write_ha_state()
