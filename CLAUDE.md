# Workflowy Home Assistant Integration - Project Context & History

## 1. Project Overview
Development and distribution of a custom Home Assistant integration for **Workflowy** (`ha-workflowy`), designed for distribution via HACS.

## 2. Key Architecture & Features
- **To-Do Platform (`todo.py`)**:
  - Full support for Home Assistant `todo` entities.
  - Multi-item batch deletion via `async_delete_todo_items`.
  - Item description/note editing via `TodoListEntityFeature.SET_DESCRIPTION_ON_ITEM` mapped to Workflowy's `note` field.
  - Triggers custom event `workflowy_todo_item_created` on task creation.
  - Local state caching to ensure smooth UI updates despite Workflowy's eventual consistency sync.
- **Sensor Platform (`sensor.py`)**:
  - Dynamically fetches and displays the exact Workflowy parent node name as entity title.
  - Native sensor value displays the total sub-item count.
- **Config & Options Flow (`config_flow.py`)**:
  - Authenticates via Workflowy API Key.
  - Interactive multi-select dropdown to choose parent nodes/folders to sync.
- **API Client (`api.py`)**:
  - Interacts with Workflowy v1 REST endpoints (`/nodes`, `/nodes/{id}/complete`, `/nodes/{id}/uncomplete`).

## 3. Current Version & Release Status
- **Repository**: `https://github.com/woldhek/ha-workflowy`
- **Latest Release Tag**: `v1.0.4`
- **Structure**:
  - `custom_components/workflowy/` (contains code, `manifest.json`, `icon.png`, `icon@2x.png`)
  - `hacs.json` (HACS configuration)
  - `README.md` (complete documentation & automation examples)
  - `.gitignore` (excludes `config/` and `__pycache__`)

## 4. Instructions for Continuing Development
If starting a new session, provide this summary or instruct the assistant to read `CLAUDE.md` / `README.md` from the repository.
