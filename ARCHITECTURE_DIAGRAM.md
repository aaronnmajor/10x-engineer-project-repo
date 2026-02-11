# Project Architecture Overview

## 1) What this app does
PromptLab is an AI Prompt Engineering Platform designed to manage and store AI prompts and collections. It provides a simple API to create, retrieve, update, and delete prompts and collections. Its primary purpose is likely to aid in the organization of prompts for AI-driven applications.

## 2) Runtime Architecture
The application operates as a FastAPI service, initiated through Uvicorn, which serves HTTP requests. When a request is received, it is processed through the FastAPI routing mechanism defined in `app/api.py`. The middleware stack, including CORS, handles pre- and post-request processing. Requests interact with the in-memory data storage implemented in `app/storage.py`.

## 3) Key Modules and Responsibilities
- **backend/main.py**: Entry point for starting the FastAPI server.
- **backend/app/api.py**: Defines API endpoints for managing prompts and collections.
- **backend/app/models.py**: Contains Pydantic models for data validation and serialization.
- **backend/app/storage.py**: Implements in-memory storage and CRUD operations for prompts and collections.
- **backend/app/utils.py**: Provides utility functions for searching and sorting prompts.

## 4) Data Model Overview
- **Prompt**: Includes fields such as `id`, `title`, `content`, `description`, `collection_id`, with timestamps for creation and update.
- **Collection**: Includes fields like `id`, `name`, `description`, and a creation timestamp.
- **Relationships**: A Prompt can be associated with a Collection via `collection_id`.

## 5) Storage Layer Overview
Data resides in an in-memory storage class (`Storage` in `storage.py`). CRUD operations interact directly with Python dictionaries. In a production system, this would be replaced with a persistent database.

## 6) API Surface Area
- **GET /health**: Returns health status.
- **Prompts**:
  - **GET /prompts**: List all prompts with optional collection filtering and search.
  - **GET /prompts/{prompt_id}**: Retrieve a specific prompt.
  - **POST /prompts**: Create a new prompt.
  - **PUT /prompts/{prompt_id}**: Update an existing prompt.
  - **DELETE /prompts/{prompt_id}**: Delete a prompt.
- **Collections**:
  - **GET /collections**: List all collections.
  - **GET /collections/{collection_id}**: Retrieve a specific collection.
  - **POST /collections**: Create a new collection.
  - **DELETE /collections/{collection_id}**: Delete a collection.

## 7) Tests
- **Location**: `backend/tests/test_api.py`
- **Structure**: Uses pytest with the FastAPI test client to test API endpoints.
- **Execution**: Run tests using `pytest`.

## 8) Common Execution Paths
- **Create Prompt**: POST to `/prompts` with prompt data.
- **Update Prompt**: PUT to `/prompts/{prompt_id}` with updated data.
- **List/Search Prompts**: GET to `/prompts` with optional filters for collection and search query.
- **Create Collection**: POST to `/collections` with collection data.

## 9) "If I only understand 5 files today, which are they and why?"
1. **backend/main.py**: Understand how the app starts and serves requests.
2. **backend/app/api.py**: Core API logic and routing definitions.
3. **backend/app/models.py**: Data models and validation logic.
4. **backend/app/storage.py**: Interaction with the storage layer, crucial for understanding data flow.
5. **backend/tests/test_api.py**: Provides insight into expected application behavior through tests.

If you wish to implement further changes based on these insights, you're ready to proceed with modifications and enhancements. The architecture gives a comprehensive view into the operational structure of PromptLab.