"""Tests for utility functions in app.utils."""

from datetime import datetime
from typing import Optional

import pytest

from app.models import Prompt
from app.utils import (
    extract_variables,
    filter_prompts_by_collection,
    search_prompts,
    sort_prompts_by_date,
    validate_prompt_content,
)


class TestValidatePromptContent:
    def test_valid_content_returns_true(self):
        """Valid content of sufficient length passes validation."""
        assert validate_prompt_content("This content is valid") is True

    def test_empty_string_returns_false(self):
        """Empty strings fail validation."""
        assert validate_prompt_content("") is False

    def test_none_returns_false(self):
        """None inputs fail validation."""
        assert validate_prompt_content(None) is False

    def test_whitespace_only_returns_false(self):
        """Whitespace-only strings fail validation."""
        assert validate_prompt_content("   \t\n  ") is False

    def test_short_content_returns_false(self):
        """Content shorter than ten characters fails validation."""
        assert validate_prompt_content("Too short") is False

    def test_exactly_ten_characters_returns_true(self):
        """Content with exactly ten characters passes validation."""
        assert validate_prompt_content("abcdefghij") is True

    def test_trimmed_whitespace_content_returns_true(self):
        """Trimmed content of sufficient length passes validation."""
        assert validate_prompt_content("   padded text   ") is True


class TestExtractVariables:
    def test_single_variable_returns_variable_name(self):
        content = "Hello {{name}}"
        assert extract_variables(content) == ["name"]

    def test_multiple_variables_returns_all_names(self):
        content = "Hello {{first_name}} and welcome to {{platform}}"
        assert extract_variables(content) == ["first_name", "platform"]

    def test_no_variables_returns_empty_list(self):
        content = "Hello world"
        assert extract_variables(content) == []

    def test_duplicate_variable_names_are_all_returned(self):
        content = "Hello {{name}} and {{name}}"
        assert extract_variables(content) == ["name", "name"]

    def test_empty_string_returns_empty_list(self):
        assert extract_variables("") == []


class TestSortPromptsByDate:
    def _build_prompt(self, title: str, created_at: datetime) -> Prompt:
        return Prompt(
            title=title,
            content=f"{title} content",
            created_at=created_at,
            updated_at=created_at,
        )

    def test_sort_descending_newest_first(self):
        older = self._build_prompt("older", datetime(2023, 1, 1, 12, 0, 0))
        newer = self._build_prompt("newer", datetime(2024, 1, 1, 12, 0, 0))

        result = sort_prompts_by_date([older, newer])

        assert result == [newer, older]

    def test_sort_ascending_oldest_first(self):
        oldest = self._build_prompt("oldest", datetime(2022, 6, 15, 8, 30, 0))
        middle = self._build_prompt("middle", datetime(2023, 6, 15, 8, 30, 0))
        newest = self._build_prompt("newest", datetime(2024, 6, 15, 8, 30, 0))

        result = sort_prompts_by_date([newest, oldest, middle], descending=False)

        assert result == [oldest, middle, newest]

    def test_empty_list_returns_empty_list(self):
        assert sort_prompts_by_date([]) == []


class TestFilterPromptsByCollection:
    def _prompt(self, title: str, collection_id: Optional[str]):
        return Prompt(
            title=title,
            content=f"{title} content",
            collection_id=collection_id,
        )

    def test_filters_matching_collection_id(self):
        marketing_prompt = self._prompt("Launch Plan", "marketing")
        support_prompt = self._prompt("Support Reply", "support")
        another_marketing_prompt = self._prompt("Campaign Brief", "marketing")

        result = filter_prompts_by_collection(
            [marketing_prompt, support_prompt, another_marketing_prompt], "marketing"
        )

        assert result == [marketing_prompt, another_marketing_prompt]

    def test_returns_empty_when_no_prompts_match(self):
        prompts = [self._prompt("General Prompt", "general")]

        assert filter_prompts_by_collection(prompts, "marketing") == []

    def test_empty_input_returns_empty_list(self):
        assert filter_prompts_by_collection([], "marketing") == []


class TestSearchPrompts:
    def _prompt(self, title: str, description: Optional[str] = None):
        return Prompt(
            title=title,
            content=f"{title} content",
            description=description,
        )

    def test_matches_on_title_case_insensitive(self):
        prompts = [
            self._prompt("Product Launch Checklist", "Steps for go-to-market"),
            self._prompt("Weekly Report", "Summarize weekly performance"),
        ]

        result = search_prompts(prompts, "launch")

        assert result == [prompts[0]]

    def test_matches_on_description_case_insensitive(self):
        prompts = [
            self._prompt("Status Update", "Prepare a LAUNCH readiness summary"),
            self._prompt("Bug Report", "Detail reproduction steps"),
        ]

        result = search_prompts(prompts, "launch")

        assert result == [prompts[0]]

    def test_returns_empty_when_no_prompts_match(self):
        prompts = [
            self._prompt("FAQ", "Answer customer questions"),
            self._prompt("Brief", "Outline campaign goals"),
        ]

        assert search_prompts(prompts, "roadmap") == []

    def test_empty_input_returns_empty_list(self):
        assert search_prompts([], "anything") == []
