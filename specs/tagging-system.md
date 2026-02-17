# Tagging System Specification for PromptLab

## Feature Overview
- **Goal**: Allow prompts to be labeled with one or more text-based tags to improve organization, discovery, and filtering within PromptLab.
- **Scope**: Extend the in-memory models, storage layer, and FastAPI endpoints to support CRUD operations that include tags, as well as querying prompts by tag combinations.
- **Constraints**:
  - Tags are simple case-insensitive strings without special formatting requirements beyond length limits.
  - Tag state is stored within each prompt (no standalone tag resource needed for the initial release).
  - Backward compatibility for prompts without tags must be preserved.

## User Stories & Acceptance Criteria

### 1. Add Tags When Creating a Prompt
- **Story**: As a user, I want to add tags while creating a prompt so that it is easier to categorize later.
- **Acceptance Criteria**:
  - `POST /prompts` accepts an optional `tags` array of strings.
  - Tags are normalized (e.g., trimmed, converted to lowercase) before storage.
  - Duplicate tags in the request are collapsed to unique values.
  - Prompt creation fails with HTTP 400 if more than `MAX_TAGS` (default 10) are provided or if any tag exceeds the maximum length (default 30 chars).

### 2. Update Tags on Existing Prompts
- **Story**: As a user, I want to update the tags on an existing prompt to reflect new categorization.
- **Acceptance Criteria**:
  - `PUT /prompts/{id}` replaces the entire tag list (full update).
  - `PATCH /prompts/{id}` can add/remove individual tags via the same `tags` array, where omitted fields leave existing tags untouched unless explicitly provided.
  - Same validation rules as create apply (normalization, max length, max count, deduplication).

### 3. Filter Prompts by Tags
- **Story**: As a user, I want to filter prompts by one or more tags so I can find relevant prompts quickly.
- **Acceptance Criteria**:
  - `GET /prompts` accepts optional `tags` query parameter (comma-separated list).
  - When multiple tags are provided, prompts must have *all* requested tags to match (logical AND) to keep semantics consistent with existing collection filtering.
  - Tag filtering can be combined with `collection_id` and `search` parameters.

## Data Model Changes

### Prompt Models (`backend/app/models.py`)
- Add `tags: List[str] = Field(default_factory=list)` to `PromptBase` so it propagates through create/update schemas.
- Update Pydantic validators or helper methods to enforce:
  - Normalization (lowercase + trim whitespace, remove empty strings).
  - Deduplication while preserving a deterministic order (e.g., sorted or insertion order post-normalization).
  - Maximum tag count (`MAX_TAGS = 10`) and per-tag length (`MAX_TAG_LENGTH = 30`).
- Ensure `Prompt`, `PromptCreate`, `PromptUpdate`, and `PromptPartialUpdate` inherit the new field.

### Storage (`backend/app/storage.py`)
- No schema change required beyond storing the updated Prompt objects, since tags live directly on the prompt instances.
- Consider helper methods for retrieving prompts by tag if reuse emerges; initially filtering can happen in the API layer for simplicity.

## API Endpoint Specifications

### POST /prompts
- **Request Body Changes**: Add optional `tags: List[str]` field.
- **Validation**: Apply tag normalization + validation before instantiating `Prompt`.
- **Response**: Returns the prompt with its normalized tag list.

### PUT /prompts/{prompt_id}
- **Request Body Changes**: Include `tags` field (required if part of `PromptUpdate` due to inheritance from `PromptBase`).
- **Behavior**: Replaces entire tag list; must pass validation. If omitted (to preserve backward compatibility), treat as empty list to align with existing model constraints.

### PATCH /prompts/{prompt_id}
- **Request Body Changes**: `tags` becomes optional; when present, replaces the tag list with the provided value after validation. When absent, existing tags remain.

### GET /prompts
- **Query Parameters**:
  - `tags`: string; comma-separated list (e.g., `tags=nlp,classification`).
- **Behavior**: After existing collection and search filtering, narrow results to prompts whose normalized tag sets include all requested tags.
- **Response**: Unchanged schema; `PromptList` now includes tag arrays per prompt.

## Search & Filter Requirements
- Tag filtering occurs after retrieving prompts from storage.
- Tag matching is case-insensitive due to normalization; API can compare normalized tags directly.
- Combine filters in the following order to minimize work on large sets:
  1. Retrieve all prompts from storage.
  2. Filter by `collection_id` (if provided).
  3. Filter by `tags` (if provided).
  4. Apply `search` across title/description/content.
  5. Sort via `sort_prompts_by_date` (existing behavior).
- Consider future extension where search includes tags (e.g., search term matches tag text); for now, tag filtering is explicit via query param only.

## Edge Cases & Validation Rules
- **Duplicate Tags**: If request provides duplicates (case-insensitive), collapse to unique values in deterministic order.
- **Whitespace Variants**: Trim whitespace, reject empty strings after trimming.
- **Case Sensitivity**: Store tags as lowercase to simplify filtering.
- **Tag Limits**: Reject requests exceeding `MAX_TAGS` or containing tags longer than `MAX_TAG_LENGTH` characters with HTTP 400 and descriptive error message.
- **Invalid Types**: Ensure tags are strings; reject numeric or null entries with validation errors.
- **Backward Compatibility**: Existing prompts without tags should serialize with `tags: []`.

## Implementation Steps Summary
1. **Model Updates**
   - Introduce constants for tag constraints in `models.py`.
   - Add `tags` field to base prompt models and ensure derived models inherit it.
   - Implement validation logic (Pydantic validators or helper functions) for normalization and constraints.

2. **Storage Layer**
   - No structural changes; ensure tests cover storing/retrieving prompts with tags.

3. **API Adjustments**
   - Update create/update/patch endpoints to rely on the new model field and ensure responses include `tags`.
   - Extend `list_prompts` to parse and apply `tags` query parameter (support comma-separated list and handle URL encoding).
   - Ensure `search_prompts` utility continues to operate unchanged but consider future updates to include tags in search results.

4. **Validation Errors**
   - Standardize error responses for invalid tag input (400 with detail string).

5. **Testing & Documentation**
   - Add unit tests for model validation, storage persistence with tags, and API endpoints covering creation, update, patch, and filtering flows.
   - Update README or API docs to mention tag functionality and usage examples.
