"""Unit tests for the in-memory storage layer."""

import pytest

from app.models import Prompt, Collection
from app.storage import storage


@pytest.fixture(autouse=True)
def clear_storage():
    """Ensure a clean storage instance before each test."""
    storage.clear()


def _build_prompt(prompt_id: str = "prompt-id", collection_id: str = None) -> Prompt:
    """Helper to create a Prompt instance for tests."""
    return Prompt(
        id=prompt_id,
        title="Sample Title",
        content="Sample content",
        collection_id=collection_id,
    )


def _build_collection(collection_id: str = "collection-id") -> Collection:
    """Helper to create a Collection instance for tests."""
    return Collection(
        id=collection_id,
        name="Sample Collection",
        description="Sample collection description",
    )


class TestStorage:
    def test_update_nonexistent_prompt(self):
        """Updating a missing prompt should return ``None``."""
        prompt = _build_prompt()

        result = storage.update_prompt("missing-id", prompt)

        assert result is None

    def test_delete_nonexistent_prompt(self):
        """Deleting a missing prompt should return ``False``."""
        assert storage.delete_prompt("missing-id") is False

    def test_delete_nonexistent_collection(self):
        """Deleting a missing collection should return ``False``."""
        assert storage.delete_collection("missing-id") is False

    def test_get_prompts_by_collection(self):
        """Only prompts matching the collection ID should be returned."""
        prompt_match_1 = _build_prompt(prompt_id="prompt-1", collection_id="collection-1")
        prompt_match_2 = _build_prompt(prompt_id="prompt-2", collection_id="collection-1")
        prompt_non_match = _build_prompt(prompt_id="prompt-3", collection_id="collection-2")

        storage.create_prompt(prompt_match_1)
        storage.create_prompt(prompt_match_2)
        storage.create_prompt(prompt_non_match)

        result = storage.get_prompts_by_collection("collection-1")

        assert {prompt.id for prompt in result} == {"prompt-1", "prompt-2"}

    def test_get_prompts_by_collection_empty(self):
        """An empty list is returned when no prompts belong to the collection."""
        storage.create_prompt(_build_prompt(prompt_id="prompt-1", collection_id="collection-2"))

        assert storage.get_prompts_by_collection("collection-1") == []

    def test_clear_storage(self):
        """Clearing storage removes prompts and collections."""
        prompt = _build_prompt(prompt_id="prompt-1", collection_id="collection-1")
        collection = _build_collection(collection_id="collection-1")

        storage.create_prompt(prompt)
        storage.create_collection(collection)

        storage.clear()

        assert storage.get_prompt(prompt.id) is None
        assert storage.get_collection(collection.id) is None
        assert storage.get_all_prompts() == []
        assert storage.get_all_collections() == []
