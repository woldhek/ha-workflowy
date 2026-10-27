# Workflowy Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

A custom Home Assistant integration that synchronizes your Workflowy lists as native Home Assistant `todo` entities and tracks item counts with `sensor` entities. This allows you to manage your Workflowy tasks directly from your Home Assistant dashboard.

## Features

- **To-do List Synchronization**: Syncs specific Workflowy nodes as Home Assistant `todo` entities.
- **Full Task Management**: Create, complete, uncomplete, rename, and delete todo items directly from Home Assistant.
- **Subtext (Note) Support**: Full support for Workflowy notes/subtexts. View, edit, and update item descriptions directly through Home Assistant.
- **Sensor Support**: Provides dedicated sensors displaying the exact item count and node name for selected parent nodes.
- **Smart Configuration**: Uses an interactive dropdown menu (Options Flow) to easily select your Workflowy nodes.
- **Multi-list Support**: Configure multiple lists by selecting several nodes in the integration options.
- **Real-time Polling**: Automatically syncs changes from Workflowy every 30 seconds.
- **Automations & Events**: Fires `workflowy_todo_item_created` events when new tasks are created for easy automation triggers.

## Requirements

- [Home Assistant](https://www.home-assistant.io/)
- A [Workflowy](https://workflowy.com/) account and an API Key.

---

## Installation

### Using HACS (Recommended)

1. Open **Home Assistant**.
2. Go to **HACS** > **Integrations**.
3. Click the three dots in the top right corner and select **Custom repositories**.
4. Paste the GitHub repository URL: `https://github.com/woldhek/ha-workflowy`
5. Select **Integration** as the category and click **Add**.
6. Search for **Workflowy Integration** and click **Download**.
7. Restart Home Assistant.

### Manual Installation

1. Download the latest release from [GitHub Releases](https://github.com/woldhek/ha-workflowy/releases).
2. Copy the `custom_components/workflowy` directory into your Home Assistant `config/custom_components/` folder.
3. Restart Home Assistant.

---

## Configuration

After installation, follow these steps to configure the integration:

1. Go to **Settings** > **Devices & Services**.
2. Click **Add Integration**.
3. Search for **Workflowy** and select it.
4. Enter your **Workflowy API Key**.

### Selecting Lists (Options Flow)

The integration uses an interactive UI to help you pick which lists to sync:

1. Go to **Settings** > **Devices & Services**.
2. Find the Workflowy integration and click **Configure**.
3. A dropdown menu will appear, automatically fetching your Workflowy nodes.
4. Select one or multiple nodes from the list (including the "Root" node).
5. Click **Submit** to apply changes.

---

## Fired Events

When a to-do item is created via Home Assistant, the integration fires a Home Assistant bus event:

- **Event Name**: `workflowy_todo_item_created`
- **Event Data**:
  ```yaml
  entity_id: todo.workflowy_boodschappen
  summary: Melk halen
  description: 2 pakken volle melk
  item_id: 3a5d-4b4d-9953
  parent_node_id: c3c0c941b720

--- 
### Example Automation Trigger
```yaml
alias: "Notify when Workflowy item added"
trigger:
  - platform: event
    event_type: workflowy_todo_item_created
action:
  - service: notify.notify
    data:
      message: "New task created: {{ trigger.event.data.summary }}
```
---
## License
This project is licensed under the MIT License - see the LICENSE file for details.