# PromptLab

FastAPI-based prompt engineering platform for creating, organizing, and testing reusable prompt templates.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Key Features](#key-features)
3. [Architecture](#architecture)
4. [Prerequisites & Installation](#prerequisites--installation)
5. [Quick Start](#quick-start)
6. [Docker](#docker)
7. [API Summary](#api-summary)
8. [Development Setup](#development-setup)
9. [Contributing](#contributing)
10. [License](#license)

---

## Project Overview

PromptLab is an internal productivity tool that helps AI engineers build a shared library of prompts. It ships with a FastAPI backend, Pydantic models, and a lightweight in-memory storage layer so teams can rapidly prototype prompt workflows before adopting persistent databases. The service exposes REST endpoints for CRUD operations on prompts and collections, plus utilities such as search, filtering, and health monitoring.

---

## Key Features

- **Prompt Management** – Create, update, partially update, delete, and list prompts.
- **Collections** – Group prompts into themed collections for easy discovery.
- **Search & Filtering** – Filter prompts by collection or keyword with utility helpers.
- **Timestamping & IDs** – Pydantic models auto-generate UUIDs and creation/update timestamps.
- **Health Monitoring** – `/health` endpoint exposes service status and git version.
- **Extensible Storage Layer** – Swappable in-memory store that can be replaced with a database.
- **FastAPI Tooling** – Automatic OpenAPI docs, interactive Swagger UI, and validation.

---

## Architecture

```
promptlab/
├── backend/
│   ├── app/
│   │   ├── api.py        # FastAPI routers and request handlers
│   │   ├── models.py     # Pydantic schemas and helpers
│   │   ├── storage.py    # In-memory repositories for prompts & collections
│   │   └── utils.py      # Filtering, sorting, and search helpers
│   ├── main.py           # FastAPI entrypoint
│   ├── requirements.txt  # Backend dependencies
│   └── tests/            # pytest suite
├── docs/                 # Product & API documentation (future)
├── specs/                # Functional specs (future)
└── frontend/             # React application (future)
```

---

## Prerequisites & Installation

| Tool        | Version   | Notes                           |
|-------------|-----------|---------------------------------|
| Python      | 3.10 or + | Required for the FastAPI app    |
| pip         | Latest    | Used to install dependencies    |
| Node.js     | 18 or +   | Reserved for the frontend phase |
| Git         | 2.40 or + | Version control                  |

### Clone and Install

```bash
# Clone the repo
git clone <your-repo-url>
cd promptlab

# Create virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install backend dependencies
cd backend
pip install -r requirements.txt
```

---

## Quick Start

1. **Run the API**
   ```bash
   uvicorn app.api:app --reload
   ```
   - REST API: http://localhost:8000
   - Docs (Swagger UI): http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

2. **Seed Example Data (optional)**
   - Use the `/collections` and `/prompts` POST endpoints or `app.storage.storage` in an interactive shell to insert sample items.

3. **Run Tests**
   ```bash
   pytest -v
   ```

---

## Docker

Use Docker Compose to build and run the FastAPI backend without installing Python locally:

1. **Build & Start the Service**
   ```bash
   docker compose up --build backend
   ```

2. **Access the API** – http://localhost:8000 (Swagger UI at `/docs`).

3. **Stop the Containers**
   ```bash
   docker compose down
   ```

---

## API Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/health` | Health status + version metadata |
| GET    | `/prompts` | List prompts, with optional `collection_id` and `search` filters |
| GET    | `/prompts/{prompt_id}` | Retrieve a specific prompt |
| POST   | `/prompts` | Create a new prompt |
| PUT    | `/prompts/{prompt_id}` | Replace an existing prompt |
| PATCH  | `/prompts/{prompt_id}` | Partially update prompt fields |
| DELETE | `/prompts/{prompt_id}` | Delete a prompt |
| GET    | `/collections` | List all collections |
| GET    | `/collections/{collection_id}` | Retrieve a collection |
| POST   | `/collections` | Create a collection |
| DELETE | `/collections/{collection_id}` | Delete a collection (prompts are disassociated) |

### Example Requests & Responses

<details>
<summary><strong>GET /health</strong></summary>

**Request**

```bash
curl http://localhost:8000/health
```

**Response**

```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```
</details>

<details>
<summary><strong>POST /collections</strong></summary>

**Request**

```bash
curl -X POST \
  http://localhost:8000/collections \
  -H "Content-Type: application/json" \
  -d '{"name": "Productivity", "description": "Prompts for focus"}'
```

**Response**

```json
{
  "id": "f2c4...",
  "name": "Productivity",
  "description": "Prompts for focus",
  "created_at": "2024-05-01T12:00:00"
}
```
</details>

<details>
<summary><strong>POST /prompts</strong></summary>

**Request**

```bash
curl -X POST \
  http://localhost:8000/prompts \
  -H "Content-Type: application/json" \
  -d '{
        "title": "Summarize an article",
        "content": "Summarize the provided text in 3 bullets.",
        "description": "General summarization guidance",
        "collection_id": "f2c4..."
      }'
```

**Response**

```json
{
  "id": "0c74...",
  "title": "Summarize an article",
  "content": "Summarize the provided text in 3 bullets.",
  "description": "General summarization guidance",
  "collection_id": "f2c4...",
  "created_at": "2024-05-01T12:05:00",
  "updated_at": "2024-05-01T12:05:00"
}
```
</details>

<details>
<summary><strong>PATCH /prompts/{prompt_id}</strong></summary>

**Request**

```bash
curl -X PATCH \
  http://localhost:8000/prompts/0c74... \
  -H "Content-Type: application/json" \
  -d '{"description": "Updated with tone guidance"}'
```

**Response**

```json
{
  "id": "0c74...",
  "title": "Summarize an article",
  "content": "Summarize the provided text in 3 bullets.",
  "description": "Updated with tone guidance",
  "collection_id": "f2c4...",
  "created_at": "2024-05-01T12:05:00",
  "updated_at": "2024-05-01T12:10:32"
}
```
</details>

<details>
<summary><strong>DELETE /collections/{collection_id}</strong></summary>

**Behavior**
- Disassociates prompts in the collection by setting their `collection_id` to `null` before removing the collection.

**Request**

```bash
curl -X DELETE http://localhost:8000/collections/f2c4...
```

**Response**

```
204 No Content
```
</details>

---

## Development Setup

1. **Environment Variables** – No secrets required for in-memory mode. Add `.env` if you later integrate databases or APIs.
2. **Code Quality**
   - Format: `ruff format` or `black` (choose one for your workflow).
   - Lint: `ruff check` or `flake8`.
3. **Reloading** – Use `uvicorn --reload` for hot reload during API development.
4. **Testing** – Add new pytest cases under `backend/tests/`. Keep fixtures in `conftest.py`.
5. **Data Layer Swap** – Replace `Storage` in `app/storage.py` with your preferred persistence mechanism without touching the API surface.

---

## Contributing

1. **Fork** the repository or create a feature branch.
2. **Create an Issue** describing the change or bug fix.
3. **Develop** your feature:
   - Follow existing code style and Pydantic/FastAPI best practices.
   - Add or update tests for any new behavior.
4. **Run Tests & Linters** before pushing.
5. **Submit a Pull Request** with a clear summary, screenshots (if applicable), and testing notes.
6. **Code Review** – Address feedback promptly to keep the release pipeline moving.

---

## License

This project is currently proprietary and intended for internal PromptLab experimentation. Contact the maintainers before distributing outside the organization.
