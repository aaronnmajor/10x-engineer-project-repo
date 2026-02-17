"""Utility functions for PromptLab"""

from typing import List
from app.models import Prompt


def sort_prompts_by_date(prompts: List[Prompt], descending: bool = True) -> List[Prompt]:
    """Sort prompts by creation date.

    Args:
        prompts (List[Prompt]): Collection of prompts to sort.
        descending (bool): Whether to order from newest to oldest.

    Returns:
        List[Prompt]: Prompts ordered by their ``created_at`` timestamp.

    Example:
        >>> sort_prompts_by_date([prompt_old, prompt_new])[0]
        prompt_new
    """
    
    return sorted(prompts, key=lambda p: p.created_at, reverse=descending)


def filter_prompts_by_collection(prompts: List[Prompt], collection_id: str) -> List[Prompt]:
    """Filter prompts by associated collection identifier.

    Args:
        prompts (List[Prompt]): Collection of prompts to evaluate.
        collection_id (str): Identifier of the collection to retain.

    Returns:
        List[Prompt]: Prompts whose ``collection_id`` matches ``collection_id``.

    Example:
        >>> filter_prompts_by_collection(prompts, "marketing")
        [prompt_a, prompt_c]
    """

    return [p for p in prompts if p.collection_id == collection_id]


def search_prompts(prompts: List[Prompt], query: str) -> List[Prompt]:
    """Search prompts by title or description.

    Args:
        prompts (List[Prompt]): Collection of prompts to crawl.
        query (str): Search text used to match against titles and descriptions.

    Returns:
        List[Prompt]: Prompts whose title or description contains the query (case-insensitive).

    Example:
        >>> search_prompts(prompts, "launch")
        [prompt_launch_plan]
    """

    query_lower = query.lower()
    return [
        p for p in prompts 
        if query_lower in p.title.lower() or 
           (p.description and query_lower in p.description.lower())
    ]


def validate_prompt_content(content: str) -> bool:
    """Validate that prompt content meets minimum requirements.

    Args:
        content (str): Prompt body text to validate.

    Returns:
        bool: True if content is non-empty, non-whitespace, and at least 10 characters long.

    Example:
        >>> validate_prompt_content("Describe the user persona.")
        True
    """
    if not content or not content.strip():
        return False
    return len(content.strip()) >= 10


def extract_variables(content: str) -> List[str]:
    """Extract template variables from prompt content.

    Variables are expected to follow the ``{{variable_name}}`` format.

    Args:
        content (str): Prompt text that may contain ``{{variable}}`` tokens.

    Returns:
        List[str]: Variable names found within the prompt content.

    Example:
        >>> extract_variables("Hello {{name}}, welcome to {{platform}}!")
        ['name', 'platform']
    """
    import re
    pattern = r'\{\{(\w+)\}\}'
    return re.findall(pattern, content)

