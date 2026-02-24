"""Tests for prompt versioning functionality (TDD red phase).

These tests describe the expected behavior for the upcoming prompt
versioning system described in ``specs/prompt-versions.md``. They are
expected to fail until the feature is implemented.
"""


class TestAutoVersioning:
    """Integration tests covering automatic prompt version tracking."""

    def test_create_prompt_creates_version_one(self, client, sample_prompt_data):
        """Creating a prompt should record version 1 automatically."""
        create_response = client.post("/prompts", json=sample_prompt_data)
        assert create_response.status_code == 201
        prompt_id = create_response.json()["id"]

        version_response = client.get(f"/prompts/{prompt_id}/versions/1")
        assert version_response.status_code == 200
        version = version_response.json()
        assert version["version_number"] == 1
        assert version["content"] == sample_prompt_data["content"]

    def test_get_versions_lists_history_with_version_one(self, client, sample_prompt_data):
        """Version history endpoint should return the initial version."""
        create_response = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create_response.json()["id"]

        history_response = client.get(f"/prompts/{prompt_id}/versions")
        assert history_response.status_code == 200
        history = history_response.json()

        assert history["total"] == 1
        assert len(history["versions"]) == 1
        assert history["versions"][0]["version_number"] == 1

    def test_put_update_creates_version_two(self, client, sample_prompt_data):
        """Full updates should append a new prompt version."""
        create_response = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create_response.json()["id"]

        updated_payload = {
            "title": "Updated Prompt",
            "content": "Updated prompt body",
            "description": "Updated description",
        }
        update_response = client.put(f"/prompts/{prompt_id}", json=updated_payload)
        assert update_response.status_code == 200

        history_response = client.get(f"/prompts/{prompt_id}/versions")
        assert history_response.status_code == 200
        history = history_response.json()

        assert history["total"] == 2
        latest_version = history["versions"][0]
        assert latest_version["version_number"] == 2
        assert latest_version["title"] == updated_payload["title"]

    def test_patch_update_creates_new_version(self, client, sample_prompt_data):
        """Partial updates should also create a new version."""
        create_response = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create_response.json()["id"]

        patch_payload = {"title": "Patched Title"}
        patch_response = client.patch(f"/prompts/{prompt_id}", json=patch_payload)
        assert patch_response.status_code == 200

        history_response = client.get(f"/prompts/{prompt_id}/versions")
        assert history_response.status_code == 200
        history = history_response.json()

        assert history["total"] == 2
        assert history["versions"][0]["version_number"] == 2
        assert history["versions"][0]["title"] == patch_payload["title"]

    def test_versions_capture_historical_content(self, client, sample_prompt_data):
        """Each version should preserve the prompt content at that time."""
        create_response = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create_response.json()["id"]

        put_payload = {
            "title": "Second Version",
            "content": "Second version content",
            "description": "Updated description",
        }
        client.put(f"/prompts/{prompt_id}", json=put_payload)

        patch_payload = {"content": "Third version content"}
        client.patch(f"/prompts/{prompt_id}", json=patch_payload)

        history_response = client.get(
            f"/prompts/{prompt_id}/versions",
            params={"order": "asc"},
        )
        assert history_response.status_code == 200
        versions = history_response.json()["versions"]

        contents = [version["content"] for version in versions]
        assert contents == [
            sample_prompt_data["content"],
            put_payload["content"],
            patch_payload["content"],
        ]


class TestVersionRetrieval:
    """Integration tests covering prompt version retrieval endpoints."""

    def test_get_versions_returns_newest_first(self, client, sample_prompt_data):
        """Version listings should present the newest version first by default."""
        create_response = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create_response.json()["id"]

        second_version_payload = {
            "title": "Second Version",
            "content": "Content for version two",
            "description": "Updated description",
        }
        client.put(f"/prompts/{prompt_id}", json=second_version_payload)

        third_version_payload = {"content": "Content for version three"}
        client.patch(f"/prompts/{prompt_id}", json=third_version_payload)

        history_response = client.get(f"/prompts/{prompt_id}/versions")
        assert history_response.status_code == 200
        versions = history_response.json()["versions"]

        version_numbers = [version["version_number"] for version in versions]
        assert version_numbers == [3, 2, 1]

    def test_get_specific_version_returns_requested_snapshot(self, client, sample_prompt_data):
        """Fetching a specific version number should return that version's data."""
        create_response = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create_response.json()["id"]

        update_payload = {
            "title": "Updated Prompt Title",
            "content": "Updated prompt content",
            "description": "Updated description",
        }
        client.put(f"/prompts/{prompt_id}", json=update_payload)

        version_response = client.get(f"/prompts/{prompt_id}/versions/2")
        assert version_response.status_code == 200
        version = version_response.json()

        assert version["version_number"] == 2
        assert version["title"] == update_payload["title"]
        assert version["content"] == update_payload["content"]

    def test_get_unknown_version_returns_404(self, client, sample_prompt_data):
        """Requesting a version that does not exist should return 404."""
        create_response = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create_response.json()["id"]

        missing_version_response = client.get(f"/prompts/{prompt_id}/versions/999")
        assert missing_version_response.status_code == 404

    def test_get_versions_for_nonexistent_prompt_returns_404(self, client):
        """Version listing for an unknown prompt should return 404."""
        response = client.get("/prompts/nonexistent-id/versions")
        assert response.status_code == 404


class TestVersionRevert:
    """Integration tests covering prompt revert behavior."""

    def test_revert_creates_new_version_with_old_content(self, client, sample_prompt_data):
        """Reverting should snapshot the historical version as a new latest entry."""
        create_response = client.post("/prompts", json=sample_prompt_data)
        assert create_response.status_code == 201
        prompt_id = create_response.json()["id"]

        updated_payload = {
            "title": "Updated Prompt",
            "content": "Updated prompt body",
            "description": "Updated description",
        }
        update_response = client.put(f"/prompts/{prompt_id}", json=updated_payload)
        assert update_response.status_code == 200

        revert_response = client.post(f"/prompts/{prompt_id}/versions/1/revert")
        assert revert_response.status_code == 200

        history_response = client.get(f"/prompts/{prompt_id}/versions")
        assert history_response.status_code == 200
        history = history_response.json()

        assert history["total"] == 3
        latest_version = history["versions"][0]
        assert latest_version["version_number"] == 3
        assert latest_version["content"] == sample_prompt_data["content"]

    def test_revert_updates_prompt_current_content(self, client, sample_prompt_data):
        """After a revert, the prompt's current state should match the target version."""
        create_response = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create_response.json()["id"]

        put_payload = {
            "title": "Second Title",
            "content": "Second version content",
            "description": "Updated description",
        }
        client.put(f"/prompts/{prompt_id}", json=put_payload)

        revert_response = client.post(f"/prompts/{prompt_id}/versions/1/revert")
        assert revert_response.status_code == 200

        prompt_response = client.get(f"/prompts/{prompt_id}")
        assert prompt_response.status_code == 200
        prompt = prompt_response.json()

        assert prompt["content"] == sample_prompt_data["content"]
        assert prompt["title"] == sample_prompt_data["title"]

    def test_revert_unknown_version_returns_404(self, client, sample_prompt_data):
        """Reverting to a version that does not exist should return 404."""
        create_response = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create_response.json()["id"]

        revert_response = client.post(f"/prompts/{prompt_id}/versions/999/revert")
        assert revert_response.status_code == 404


class TestVersionCleanup:
    """Integration tests covering cleanup of version history."""

    def test_delete_prompt_removes_versions(self, client, sample_prompt_data):
        """Deleting a prompt should also remove its version history."""
        create_response = client.post("/prompts", json=sample_prompt_data)
        assert create_response.status_code == 201
        prompt_id = create_response.json()["id"]

        delete_response = client.delete(f"/prompts/{prompt_id}")
        assert delete_response.status_code == 204

        versions_response = client.get(f"/prompts/{prompt_id}/versions")
        assert versions_response.status_code == 404
