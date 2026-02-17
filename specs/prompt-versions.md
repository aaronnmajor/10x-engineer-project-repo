# Prompt Version Tracking Specification

## Feature Overview

Introduce first-class version tracking for prompts so that every change to a prompt is captured, reviewable, and reversible. Each prompt will maintain a chronological history of versions containing its content, metadata, authoring information (if available), and timestamps. The API should allow clients to:

- Retrieve the version history for a prompt with pagination.
- Inspect a specific version.
- Create a new version by updating a prompt (full or partial update).
- Revert a prompt to a previous version.
- Enforce optional limits (e.g., max versions per prompt) with configurable pruning.

The feature builds upon the existing in-memory storage patterns (`app/storage.py`) and Pydantic models (`app/models.py`).

## User Stories & Acceptance Criteria

### 1. Record Prompt Versions Automatically
- **Story:** As a PromptLab user, whenever I create or update a prompt, I want the system to capture the new state as a version so that I can audit changes later.
- **Acceptance Criteria:**
  - Creating a prompt stores Version 1 automatically.
  - PUT/PATCH requests append a new version with incremented version numbers.
  - Version entries store `title`, `content`, `description`, `collection_id`, `created_at`, `updated_at`, and `version_created_at` timestamps.

### 2. View Version History
- **Story:** As a user, I want to list all versions of a prompt to understand its evolution.
- **Acceptance Criteria:**
  - `GET /prompts/{prompt_id}/versions` returns versions sorted newest-first by default, with pagination parameters (`limit`, `offset`).
  - Response includes metadata: `version_number`, `updated_by` (optional, placeholder for future auth), and timestamps.
  - 404 returned if prompt does not exist.

### 3. Inspect a Specific Version
- **Story:** As a user, I want to fetch the details of a single version.
- **Acceptance Criteria:**
  - `GET /prompts/{prompt_id}/versions/{version_number}` returns that version’s full payload.
  - 404 returned if prompt or version does not exist.

### 4. Revert to a Previous Version
- **Story:** As a user, I want to revert a prompt to any prior version when a change needs rollback.
- **Acceptance Criteria:**
  - `POST /prompts/{prompt_id}/versions/{version_number}/revert` replaces the current prompt state with the selected version and records a new version entry (with incremented number) reflecting the revert.
  - Validation ensures the target version exists; 400 returned if revert would exceed version limit (when configured).

### 5. Version Limits & Pruning
- **Story:** As an operator, I want to cap stored versions per prompt to control memory usage.
- **Acceptance Criteria:**
  - Configurable `MAX_VERSIONS_PER_PROMPT` (e.g., env var or settings module value) defaulting to `None` (unlimited).
  - When exceeding the limit, oldest versions are pruned after successfully storing the new version.
  - Pruning is logged (placeholder) and does not affect prompt integrity.

## Data Model Changes

### Pydantic Models (`app/models.py`)
- **New Models:**
  - `PromptVersionBase`: captures shared version fields (`prompt_id`, `version_number`, `title`, `content`, `description`, `collection_id`, `updated_at`, `updated_by` (Optional[str], default None)).
  - `PromptVersion`: extends base with `id` (UUID), `version_created_at` timestamp, and `from_attributes = True`.
  - `PromptVersionList`: similar to `PromptList`, includes `versions: List[PromptVersion]` and `total`.
- **Prompt Update Hooks:** No structural change to `Prompt`, but docstrings should mention version creation on modification.

### Storage Layer (`app/storage.py`)
- Add `_prompt_versions: Dict[str, List[PromptVersion]]` keyed by `prompt_id`.
- New methods:
  - `append_prompt_version(prompt_version: PromptVersion) -> PromptVersion` to store a version and enforce limits.
  - `get_prompt_versions(prompt_id: str) -> List[PromptVersion]`.
  - `get_prompt_version(prompt_id: str, version_number: int) -> Optional[PromptVersion]`.
  - `revert_prompt_to_version(prompt_id: str, version_number: int) -> Prompt` (helper to encapsulate revert logic and version recording).
  - `prune_prompt_versions(prompt_id: str)` (internal) to drop oldest versions beyond the configured limit.
- `clear()` should also wipe `_prompt_versions`.

### Configuration
- Introduce `settings.py` or use existing config pattern to manage `MAX_VERSIONS_PER_PROMPT`. For in-memory prototype, a module-level constant in `storage.py` is acceptable but should be easily adjustable.

## API Endpoint Specifications

### Existing Endpoints Modifications
- `POST /prompts`: After creating the prompt, create Version 1 capturing the initial state.
- `PUT /prompts/{prompt_id}` and `PATCH /prompts/{prompt_id}`: After storing the updated prompt, append a new version with `version_number = previous_version_number + 1`.
- Consider returning `latest_version_number` in Prompt responses (optional, but useful). Could add field `version` to `Prompt` response model referencing latest version number.

### New Endpoints
1. `GET /prompts/{prompt_id}/versions`
   - **Query Params:** `limit` (int, default 20), `offset` (int, default 0), `order` (enum: `desc` default, `asc`).
   - **Response Model:** `PromptVersionList`.
   - **Errors:** 404 if prompt not found.

2. `GET /prompts/{prompt_id}/versions/{version_number}`
   - **Response:** `PromptVersion`.
   - **Errors:** 404 for missing prompt or version.

3. `POST /prompts/{prompt_id}/versions/{version_number}/revert`
   - **Body:** Optional metadata (e.g., `reason: Optional[str]`). For now, no body required.
   - **Response:** Updated `Prompt` with new latest version.
   - **Side Effects:** Creates new version entry representing the revert operation.
   - **Errors:** 404 if prompt/version missing, 400 if revert prohibited (e.g., limit issues) or if version is already latest and revert would be a no-op (optional rule).

## Edge Cases & Considerations

- **Concurrent Updates (Future):** Current in-memory storage is not concurrent-safe; document that version numbers assume single-threaded execution.
- **Reverting to Non-Existing Version:** Must return 404 without modifying state.
- **Reverting to Latest Version:** Allowed but should still produce a new version indicating revert action, or alternatively respond 400; clarify desired UX (recommend allowing and documenting behavior).
- **Maximum Versions:** If limit reached, ensure pruning happens after new version is appended so revert target remains available when possible. Provide deterministic pruning order (oldest first).
- **Deleted Collections:** Historical versions may reference collection IDs that no longer exist; versions should retain original metadata without validation to preserve history.
- **Prompt Deletion:** Should also delete its version history to prevent orphaned data.
- **Partial Updates:** Ensure null fields are treated correctly; partial updates should not set unspecified fields to None during version capture.
- **Timestamps:** `version_created_at` should reflect the moment the version snapshot was recorded, distinct from `updated_at` (which mirrors the prompt’s `updated_at`).

## Implementation Steps

1. **Model Updates:**
   - Extend `app/models.py` with version-related models and optional `version` field on `Prompt`.

2. **Storage Enhancements:**
   - Add `_prompt_versions` structure and supporting methods for storing, retrieving, pruning, and reverting versions.
   - Ensure `clear()` resets versions and `delete_prompt()` removes associated history.

3. **API Adjustments:**
   - Update existing prompt creation/update endpoints to append versions via new storage helpers.
   - Implement new endpoints for listing versions, fetching a version, and reverting.
   - Wire response models and error handling consistent with existing patterns (e.g., using `HTTPException`).

4. **Utilities:**
   - If needed, add helper functions for pagination and ordering of versions (similar to `sort_prompts_by_date`).

5. **Tests / Validation (future scope):**
   - Add unit tests covering version creation, retrieval, limit enforcement, and revert behavior.

6. **Documentation:**
   - Update README or API docs to describe versioning endpoints and workflows.

This specification provides the blueprint for integrating prompt version tracking while staying aligned with the current FastAPI + Pydantic architecture. Implement incrementally to maintain simplicity while enabling future persistence backends.
