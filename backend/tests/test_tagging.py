"""Tagging feature tests for PromptLab API."""

from fastapi.testclient import TestClient


class TestTagCreation:
    """Tests covering prompt creation with tagging behavior."""

    def test_create_prompt_with_tags(self, client: TestClient, sample_prompt_data):
        payload = {**sample_prompt_data, "tags": ["python", "ai"]}

        response = client.post("/prompts", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["tags"] == ["python", "ai"]

    def test_create_prompt_without_tags_defaults_empty_list(self, client: TestClient, sample_prompt_data):
        response = client.post("/prompts", json=sample_prompt_data)

        assert response.status_code == 201
        data = response.json()
        assert data["tags"] == []

    def test_tags_are_normalized(self, client: TestClient, sample_prompt_data):
        payload = {**sample_prompt_data, "tags": [" Python "]}

        response = client.post("/prompts", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["tags"] == ["python"]

    def test_duplicate_tags_removed(self, client: TestClient, sample_prompt_data):
        payload = {**sample_prompt_data, "tags": ["python", "Python", "python"]}

        response = client.post("/prompts", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["tags"] == ["python"]


class TestTagUpdates:
    """Tests covering tag behavior during prompt updates."""

    def test_put_update_replaces_entire_tag_list(self, client: TestClient, sample_prompt_data):
        create_payload = {**sample_prompt_data, "tags": ["python", "ai"]}
        create_response = client.post("/prompts", json=create_payload)
        assert create_response.status_code == 201
        prompt_id = create_response.json()["id"]

        update_payload = {
            **sample_prompt_data,
            "title": "Updated Title",
            "content": "Updated content for tag replacement",
            "description": "Updated description",
            "tags": ["rust", "systems"],
        }

        response = client.put(f"/prompts/{prompt_id}", json=update_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["tags"] == ["rust", "systems"]

    def test_patch_with_tags_field_replaces_tags(self, client: TestClient, sample_prompt_data):
        create_payload = {**sample_prompt_data, "tags": ["python", "ai"]}
        create_response = client.post("/prompts", json=create_payload)
        prompt_id = create_response.json()["id"]

        patch_payload = {"tags": ["ml", "nlp"]}
        response = client.patch(f"/prompts/{prompt_id}", json=patch_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["tags"] == ["ml", "nlp"]
        assert data["title"] == sample_prompt_data["title"]

    def test_patch_without_tags_field_preserves_existing_tags(self, client: TestClient, sample_prompt_data):
        create_payload = {**sample_prompt_data, "tags": ["python", "ai"]}
        create_response = client.post("/prompts", json=create_payload)
        prompt_id = create_response.json()["id"]

        patch_payload = {"description": "Updated description without touching tags"}
        response = client.patch(f"/prompts/{prompt_id}", json=patch_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated description without touching tags"
        assert data["tags"] == ["python", "ai"]


class TestTagFiltering:
    """Tests covering prompt retrieval filtered by tags."""

    def test_get_prompts_filtered_by_single_tag(self, client: TestClient, sample_prompt_data):
        python_prompt_payload = {
            **sample_prompt_data,
            "title": "Python Prompt",
            "content": "Content for python-specific prompt",
            "description": "Python prompt description",
            "tags": ["python", "ai"],
        }
        other_prompt_payload = {
            **sample_prompt_data,
            "title": "Rust Prompt",
            "content": "Content for rust-specific prompt",
            "description": "Rust prompt description",
            "tags": ["rust"],
        }

        python_response = client.post("/prompts", json=python_prompt_payload)
        other_response = client.post("/prompts", json=other_prompt_payload)

        assert python_response.status_code == 201
        assert other_response.status_code == 201

        response = client.get("/prompts", params={"tags": "python"})

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert {prompt["title"] for prompt in data} == {"Python Prompt"}

    def test_get_prompts_filtered_by_multiple_tags_and_logic(self, client: TestClient, sample_prompt_data):
        both_tags_payload = {
            **sample_prompt_data,
            "title": "Python AI Prompt",
            "content": "Prompt tagged with python and ai",
            "description": "Prompt requiring both tags",
            "tags": ["python", "ai"],
        }
        single_tag_payload = {
            **sample_prompt_data,
            "title": "Python Only Prompt",
            "content": "Prompt tagged only with python",
            "description": "Prompt requiring single tag",
            "tags": ["python"],
        }

        both_tags_response = client.post("/prompts", json=both_tags_payload)
        single_tag_response = client.post("/prompts", json=single_tag_payload)

        assert both_tags_response.status_code == 201
        assert single_tag_response.status_code == 201

        response = client.get("/prompts", params={"tags": "python,ai"})

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert {prompt["title"] for prompt in data} == {"Python AI Prompt"}

    def test_get_prompts_filtered_by_missing_tags_returns_empty_list(self, client: TestClient, sample_prompt_data):
        existing_prompt_payload = {
            **sample_prompt_data,
            "title": "Existing Prompt",
            "content": "Existing prompt content",
            "description": "Prompt with real tags",
            "tags": ["python"],
        }

        response = client.post("/prompts", json=existing_prompt_payload)
        assert response.status_code == 201

        filtered_response = client.get("/prompts", params={"tags": "nonexistent"})

        assert filtered_response.status_code == 200
        assert filtered_response.json() == []


class TestTagValidation:
    """Tests covering tag validation constraints."""

    def test_create_prompt_with_more_than_ten_tags_returns_422(self, client: TestClient, sample_prompt_data):
        payload = {**sample_prompt_data, "tags": [f"tag{i}" for i in range(11)]}

        response = client.post("/prompts", json=payload)

        assert response.status_code == 422

    def test_create_prompt_with_tag_longer_than_thirty_characters_returns_422(self, client: TestClient, sample_prompt_data):
        payload = {**sample_prompt_data, "tags": ["a" * 31]}

        response = client.post("/prompts", json=payload)

        assert response.status_code == 422

    def test_create_prompt_with_empty_string_tag_returns_422(self, client: TestClient, sample_prompt_data):
        payload = {**sample_prompt_data, "tags": [""]}

        response = client.post("/prompts", json=payload)

        assert response.status_code == 422
