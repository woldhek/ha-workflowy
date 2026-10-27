"""API client for Workflowy integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp

from .const import WORKFLOWY_API_BASE_URL

_LOGGER = logging.getLogger(__name__)


class WorkflowyApiClient:
    """Client for interacting with Workflowy API."""

    def __init__(self, api_key: str, session: aiohttp.ClientSession | None = None) -> None:
        """Initialize the API client."""
        self._api_key = api_key
        self._session = session or aiohttp.ClientSession()
        self._headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    async def async_get_items(self, parent_node_id: str = "") -> list[dict[str, Any]]:
        """Fetch items from Workflowy."""
        url = f"{WORKFLOWY_API_BASE_URL}/nodes"
        params = {"parent_id": parent_node_id} if parent_node_id else {}
        async with self._session.get(url, headers=self._headers, params=params) as resp:
            resp.raise_for_status()
            data = await resp.json()
            return data.get("nodes", [])

    async def async_get_node(self, node_id: str) -> dict[str, Any] | None:
        """Fetch a specific node by ID to get its metadata/name."""
        url = f"{WORKFLOWY_API_BASE_URL}/nodes/{node_id}"
        async with self._session.get(url, headers=self._headers) as resp:
            if resp.status == 200:
                return await resp.json()
            return None

    async def async_create_item(self, summary: str, note: str | None = None, parent_node_id: str = "") -> dict[str, Any]:
        """Create a new item in Workflowy."""
        url = f"{WORKFLOWY_API_BASE_URL}/nodes"
        payload: dict[str, Any] = {"name": summary}
        if note:
            payload["note"] = note
        if parent_node_id:
            payload["parent_id"] = parent_node_id

        async with self._session.post(url, headers=self._headers, json=payload) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def async_update_item(
        self,
        item_id: str,
        summary: str | None = None,
        note: str | None = None,
        completed: bool | None = None,
    ) -> None:
        """Update, edit note or complete an existing item in Workflowy."""
        if completed is True:
            url = f"{WORKFLOWY_API_BASE_URL}/nodes/{item_id}/complete"
            async with self._session.post(url, headers=self._headers) as resp:
                resp.raise_for_status()
        elif completed is False:
            url = f"{WORKFLOWY_API_BASE_URL}/nodes/{item_id}/uncomplete"
            async with self._session.post(url, headers=self._headers) as resp:
                resp.raise_for_status()

        # Update node gegevens (name en/of note)
        payload: dict[str, Any] = {}
        if summary is not None:
            payload["name"] = summary
        if note is not None:
            payload["note"] = note

        if payload:
            url = f"{WORKFLOWY_API_BASE_URL}/nodes/{item_id}"
            async with self._session.post(url, headers=self._headers, json=payload) as resp:
                resp.raise_for_status()

    async def async_delete_item(self, item_id: str) -> None:
        """Delete an item in Workflowy."""
        url = f"{WORKFLOWY_API_BASE_URL}/nodes/{item_id}"
        async with self._session.delete(url, headers=self._headers) as resp:
            resp.raise_for_status()
