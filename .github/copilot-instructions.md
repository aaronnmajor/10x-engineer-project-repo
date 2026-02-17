# PromptLab Coding Standards

## 1. Project Overview & Tech Stack
- **Purpose:** PromptLab offers a FastAPI-powered backend for managing AI prompts and collections.
- **Core Modules:**
  - `backend/app/api.py` exposes REST routes.
  - `backend/app/models.py` defines Pydantic schemas.
  - `backend/app/storage.py` provides in-memory persistence.
  - `backend/app/utils.py` hosts shared helpers.
- **Tech Stack:** Python 3.11+, FastAPI, Pydantic, and in-memory storage (placeholder for future databases).

## 2. Python Code Style Conventions
- Follow **PEP 8** for formatting (4-space indentation, descriptive names, line length ≤ 100 chars when practical).
- Prefer explicit imports and avoid wildcard imports.
- Encapsulate reusable logic in helper functions within `utils.py` or well-named modules.
- Use `Optional[...]` annotations for nullable fields and include precise type hints everywhere.

## 3. FastAPI Endpoint Patterns
- Define routes in `backend/app/api.py` using the `@app.<method>` decorators.
- Always declare `response_model` for deterministic typing.
- Include Google-style docstrings that describe Args, Returns, Raises, and usage examples (see existing endpoints).
- Validate dependencies (e.g., ensure referenced collections exist) before mutating storage.
- Return meaningful HTTP status codes (`201` for creations, `204` for deletions, `404` when entities are missing, `400` for validation failures).
- Keep business logic in helper functions or storage methods; keep route handlers thin.

## 4. Pydantic Model Conventions
- Place shared attributes in `*Base` classes (`PromptBase`, `CollectionBase`).
- Inherit `Create`, `Update`, and response models from base classes to avoid duplication.
- Use `Field` for validation constraints (e.g., `min_length`, `max_length`).
- Provide default factories (`generate_id`, `get_current_time`) for identifiers and timestamps.
- Configure models returning ORM-derived data with `Config.from_attributes = True`.

## 5. Error Handling Approach
- Raise `HTTPException` with descriptive `detail` messages for API errors.
- Use `status_code=404` when an entity cannot be found, `400` for invalid references or payloads, and `500` only for unexpected server errors.
- Validate related resources (e.g., collection existence) before performing create/update operations.
- Ensure utility functions return safe defaults instead of raising unexpected errors.

## 6. Naming Conventions
- **Files:** snake_case (e.g., `storage.py`, `utils.py`) within appropriate directories.
- **Functions & Methods:** snake_case verbs describing actions (`list_prompts`, `get_collection`).
- **Classes:** PascalCase (`PromptList`, `Storage`).
- **Routes:** plural nouns for collections (`/prompts`, `/collections`) and child paths for identifiers (`/prompts/{prompt_id}`).

## 7. Documentation Requirements
- Every public function, class, and route must follow **Google-style docstrings** mirroring existing examples.
- Include Args/Returns/Raises sections and, when relevant, an `Example` block showcasing a typical call.
- Keep docstrings concise but explicit about side effects and validations.

## 8. Testing Requirements
- Add or update tests whenever modifying business logic, storage operations, or request/response contracts.
- Prefer pytest-style tests that exercise FastAPI endpoints via `TestClient` and verify validation paths.
- Cover both success scenarios and error branches (e.g., missing collections, partial updates).
- Ensure tests remain deterministic by clearing or mocking the in-memory storage between cases.
