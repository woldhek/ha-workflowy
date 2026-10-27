"""Test Workflowy API client."""
import pytest
from custom_components.workflowy.api import WorkflowyApiClient
# Mocking required for tests that hit external API endpoints
from unittest import mock
import asyncio
import aiohttp.client_exceptions

@pytest.mark.asyncio
async def test_api_client_init():
    """Test API client initialization."""
    client = WorkflowyApiClient("test_api_key")
    assert client._api_key == "test_api_key"

# --- Mocked Tests for Authentication and Entity Lifecycle ---

@pytest.mark.asyncio
async def test_authentication_success(mocker):
    """Test successful API authentication using a mocked session."""
    mock_session = mocker.patch('aiohttp.ClientSession')
    mock_response = mock.MagicMock()
    mock_response.status = 200
    mock_response.json.return_value = {"token": "test_valid_token"}

    # Configure the client session to return our mocked response for the auth endpoint
    async def _fake_request(*args, **kwargs):
        if args[0].url.path == "/auth/login":
            mock_response.status = 200
            return mock_response

    mock_session.patch('aiohttp.ClientSession.request', side_effect=_fake_request)

    client = WorkflowyApiClient("test_api_key")
    # NOTE: Assuming the client has an async authenticate method for testing purposes
    token = await client.authenticate()

    assert token == "test_valid_token"

@pytest.mark.asyncio
async def test_todo_item_lifecycle(mocker):
    """Test successful retrieval of a specific ToDo entity item using mocked API calls."""
    mock_session = mocker.patch('aiohttp.ClientSession')
    mock_response = mock.MagicMock()
    mock_response.status = 200
    # Example todo response structure
    mock_response.json.return_value = {
        "id": "todo-1",
        "title": "Buy groceries",
        "completed": False,
        "api_type": "todo"
    }

    async def _fake_request(*args, **kwargs):
        if args[0].url.path == "/todos/todo-1":
            mock_response.status = 200
            return mock_response

    # Patch the request method of the client session
    mock_session.patch('aiohttp.ClientSession.request', side_effect=_fake_request)

    client = WorkflowyApiClient("test_api_key")
    # NOTE: Assuming the client has an async get_todo_item method for testing purposes
    item = await client.get_todo_item("todo-1")

    assert item["id"] == "todo-1"
    assert item["title"] == "Buy groceries"