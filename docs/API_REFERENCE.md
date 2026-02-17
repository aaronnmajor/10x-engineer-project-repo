# PromptLab API Reference

Base URL: `http://localhost:8000`

## Authentication

Authentication is currently **not required**. All endpoints are publicly accessible. When auth is introduced in the future, clients should expect to provide the documented credentials (headers, tokens, etc.).

## Error Handling

### General Error Envelope

Most errors raised by the API conform to FastAPI's default error format:

```json docs/API_REFERENCE.md
{
  "detail": "Human-readable explanation of the failure"
}
```

### Validation Errors (422 Unprocessable Entity)

When request payloads fail validation, FastAPI returns structured validation errors:

```json docs/API_REFERENCE.md
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "title"],
      "msg": "String should have at least 1 characters",
      "input": ""
    }
  ]
}
```

### Common HTTP Status Codes

- `200 OK`: Successful read or update operations.
- `201 Created`: Resource was created successfully.
- `204 No Content`: Resource was deleted; response body is empty.
- `400 Bad Request`: Referenced resource (e.g., collection) was invalid or missing.
- `404 Not Found`: Requested resource does not exist.
- `422 Unprocessable Entity`: Request body or parameters failed validation.
- `500 Internal Server Error`: Unexpected server failure.

---

## Endpoints

### GET /health

**Description:** Returns service health information and build metadata.

**Parameters:** None.

**Request Body:** None.

**Response:** `HealthResponse`

```json docs/API_REFERENCE.md
{
  "status": "healthy",
  "version": "1.2.3"
}
```

**Error Codes:**
- `500 Internal Server Error`: Unexpected failure retrieving health metadata.

**Example:**

```bash docs/API_REFERENCE.md
curl -X GET "http://localhost:8000/health"
```

---

### GET /prompts

**Description:** Retrieve all prompts with optional collection filtering and text search.

**Parameters:**

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `collection_id` | query | string | No | Limits results to prompts belonging to the collection. |
| `search` | query | string | No | Case-insensitive search applied to title, description, and content. |

**Request Body:** None.

**Response:** `PromptList`

```json docs/API_REFERENCE.md
{
  "prompts": [
    {
      "id": "prompt-123",
      "title": "Summarize an article",
      "content": "Summarize the provided text in 3 bullet points.",
      "description": "General summarization guidance",
      "collection_id": "collection-123",
      "created_at": "2024-04-01T12:00:00Z",
      "updated_at": "2024-04-02T08:30:00Z"
    }
  ],
  "total": 1
}
```

**Error Codes:**
- `500 Internal Server Error`: An unexpected storage or filtering error occurred.

**Example:**

```bash docs/API_REFERENCE.md
curl -G "http://localhost:8000/prompts" \
  --data-urlencode "collection_id=collection-123" \
  --data-urlencode "search=chatbot"
```

---

### GET /prompts/{prompt_id}

**Description:** Fetch a single prompt by its identifier.

**Parameters:**

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `prompt_id` | path | string | Yes | Unique identifier of the prompt. |

**Request Body:** None.

**Response:** `Prompt`

```json docs/API_REFERENCE.md
{
  "id": "prompt-123",
  "title": "Summarize an article",
  "content": "Summarize the provided text in 3 bullet points.",
  "description": "General summarization guidance",
  "collection_id": "collection-123",
  "created_at": "2024-04-01T12:00:00Z",
  "updated_at": "2024-04-02T08:30:00Z"
}
```

**Error Codes:**
- `404 Not Found`: Prompt with the supplied ID does not exist.

**Example:**

```bash docs/API_REFERENCE.md
curl -X GET "http://localhost:8000/prompts/prompt-123"
```

---

### POST /prompts

**Description:** Create a new prompt.

**Parameters:** None.

**Request Body:** `PromptCreate`

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `title` | string | Yes | Human-readable prompt title (1-200 chars). |
| `content` | string | Yes | Prompt instructions/content. |
| `description` | string | No | Additional context (≤500 chars). |
| `collection_id` | string | No | Identifier of an existing collection. |

**Request Example:**

```json docs/API_REFERENCE.md
{
  "title": "Greeting",
  "content": "Say hello in a friendly tone.",
  "description": "Quick greeting snippet",
  "collection_id": "collection-123"
}
```

**Response:** `Prompt` (newly created resource)

```json docs/API_REFERENCE.md
{
  "id": "prompt-789",
  "title": "Greeting",
  "content": "Say hello in a friendly tone.",
  "description": "Quick greeting snippet",
  "collection_id": "collection-123",
  "created_at": "2024-04-05T09:15:00Z",
  "updated_at": "2024-04-05T09:15:00Z"
}
```

**Error Codes:**
- `400 Bad Request`: `collection_id` does not reference an existing collection.
- `422 Unprocessable Entity`: Payload failed validation.

**Example:**

```bash docs/API_REFERENCE.md
curl -X POST "http://localhost:8000/prompts" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Greeting",
    "content": "Say hello in a friendly tone.",
    "description": "Quick greeting snippet",
    "collection_id": "collection-123"
  }'
```

---

### PUT /prompts/{prompt_id}

**Description:** Replace an existing prompt with new field values.

**Parameters:**

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `prompt_id` | path | string | Yes | Identifier of the prompt to update. |

**Request Body:** `PromptUpdate` (same schema as `PromptCreate`)

**Request Example:**

```json docs/API_REFERENCE.md
{
  "title": "Summarize in bullet points",
  "content": "Summarize the provided text in three concise bullets.",
  "description": "Refined wording",
  "collection_id": "collection-123"
}
```

**Response:** Updated `Prompt`

```json docs/API_REFERENCE.md
{
  "id": "prompt-123",
  "title": "Summarize in bullet points",
  "content": "Summarize the provided text in three concise bullets.",
  "description": "Refined wording",
  "collection_id": "collection-123",
  "created_at": "2024-04-01T12:00:00Z",
  "updated_at": "2024-04-07T10:20:00Z"
}
```

**Error Codes:**
- `400 Bad Request`: Supplied `collection_id` does not exist.
- `404 Not Found`: Prompt not found.
- `422 Unprocessable Entity`: Payload failed validation.

**Example:**

```bash docs/API_REFERENCE.md
curl -X PUT "http://localhost:8000/prompts/prompt-123" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Summarize in bullet points",
    "content": "Summarize the provided text in three concise bullets.",
    "description": "Refined wording",
    "collection_id": "collection-123"
  }'
```

---

### PATCH /prompts/{prompt_id}

**Description:** Partially update one or more prompt fields.

**Parameters:**

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `prompt_id` | path | string | Yes | Identifier of the prompt to update. |

**Request Body:** `PromptPartialUpdate`

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `title` | string | No | New title (1-200 chars). |
| `content` | string | No | New prompt content. |
| `description` | string | No | New description (≤500 chars). |
| `collection_id` | string | No | Reassign to another collection. |

**Request Example:**

```json docs/API_REFERENCE.md
{
  "description": "Clarified use case",
  "collection_id": null
}
```

**Response:** Updated `Prompt`

```json docs/API_REFERENCE.md
{
  "id": "prompt-123",
  "title": "Summarize an article",
  "content": "Summarize the provided text in 3 bullet points.",
  "description": "Clarified use case",
  "collection_id": null,
  "created_at": "2024-04-01T12:00:00Z",
  "updated_at": "2024-04-07T11:05:00Z"
}
```

**Error Codes:**
- `404 Not Found`: Prompt not found.
- `422 Unprocessable Entity`: Payload failed validation.

**Example:**

```bash docs/API_REFERENCE.md
curl -X PATCH "http://localhost:8000/prompts/prompt-123" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Clarified use case",
    "collection_id": null
  }'
```

---

### DELETE /prompts/{prompt_id}

**Description:** Delete a prompt by ID.

**Parameters:**

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `prompt_id` | path | string | Yes | Identifier of the prompt to delete. |

**Request Body:** None.

**Response:** `204 No Content` (empty body)

**Error Codes:**
- `404 Not Found`: Prompt not found.

**Example:**

```bash docs/API_REFERENCE.md
curl -X DELETE "http://localhost:8000/prompts/prompt-123"
```

---

### GET /collections

**Description:** List all prompt collections.

**Parameters:** None.

**Request Body:** None.

**Response:** `CollectionList`

```json docs/API_REFERENCE.md
{
  "collections": [
    {
      "id": "collection-123",
      "name": "Productivity",
      "description": "Prompts designed to improve focus and organization",
      "created_at": "2024-03-30T09:45:00Z"
    }
  ],
  "total": 1
}
```

**Error Codes:**
- `500 Internal Server Error`: Unexpected collection retrieval error.

**Example:**

```bash docs/API_REFERENCE.md
curl -X GET "http://localhost:8000/collections"
```

---

### GET /collections/{collection_id}

**Description:** Retrieve a collection by its identifier.

**Parameters:**

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `collection_id` | path | string | Yes | Identifier of the collection to fetch. |

**Request Body:** None.

**Response:** `Collection`

```json docs/API_REFERENCE.md
{
  "id": "collection-123",
  "name": "Productivity",
  "description": "Prompts designed to improve focus and organization",
  "created_at": "2024-03-30T09:45:00Z"
}
```

**Error Codes:**
- `404 Not Found`: Collection not found.

**Example:**

```bash docs/API_REFERENCE.md
curl -X GET "http://localhost:8000/collections/collection-123"
```

---

### POST /collections

**Description:** Create a new collection.

**Parameters:** None.

**Request Body:** `CollectionCreate`

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | string | Yes | Collection name (1-100 chars). |
| `description` | string | No | Additional context (≤500 chars). |

**Request Example:**

```json docs/API_REFERENCE.md
{
  "name": "Productivity",
  "description": "Prompts designed to improve focus and organization"
}
```

**Response:** `Collection`

```json docs/API_REFERENCE.md
{
  "id": "collection-789",
  "name": "Productivity",
  "description": "Prompts designed to improve focus and organization",
  "created_at": "2024-04-05T10:00:00Z"
}
```

**Error Codes:**
- `422 Unprocessable Entity`: Payload failed validation.
- `500 Internal Server Error`: Persistence failed unexpectedly.

**Example:**

```bash docs/API_REFERENCE.md
curl -X POST "http://localhost:8000/collections" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Productivity",
    "description": "Prompts designed to improve focus and organization"
  }'
```

---

### DELETE /collections/{collection_id}

**Description:** Delete a collection and disassociate any prompts assigned to it (their `collection_id` is set to `null`).

**Parameters:**

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `collection_id` | path | string | Yes | Identifier of the collection to delete. |

**Request Body:** None.

**Response:** `204 No Content` (empty body)

**Error Codes:**
- `404 Not Found`: Collection not found.

**Example:**

```bash docs/API_REFERENCE.md
curl -X DELETE "http://localhost:8000/collections/collection-123"
```
