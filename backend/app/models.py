"""Pydantic models for PromptLab"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from uuid import uuid4


def generate_id() -> str:
    """Generate a unique identifier for PromptLab entities.

    Args:
        None: This helper function takes no parameters.

    Returns:
        str: A stringified UUID4 value.

    Example:
        >>> generate_id()  # doctest: +SKIP
        '550e8400-e29b-41d4-a716-446655440000'
    """

    return str(uuid4())


def get_current_time() -> datetime:
    """Return the current UTC timestamp for PromptLab models.

    Args:
        None: This helper function takes no parameters.

    Returns:
        datetime: The current UTC datetime.

    Example:
        >>> isinstance(get_current_time(), datetime)
        True
    """

    return datetime.utcnow()


def normalize_tags(
    tags: Optional[List[str]],
    *,
    allow_none: bool = False,
) -> Optional[List[str]]:
    """Normalize and validate tag values."""
    if tags is None:
        return None if allow_none else []

    if not isinstance(tags, list):
        raise ValueError("Tags must be provided as a list of strings.")

    normalized: List[str] = []
    for tag in tags:
        if not isinstance(tag, str):
            raise ValueError("Each tag must be a string.")
        cleaned = tag.strip().lower()
        if not cleaned:
            raise ValueError("Tags cannot be empty strings.")
        if len(cleaned) > 30:
            raise ValueError("Tags cannot exceed 30 characters.")
        if cleaned not in normalized:
            normalized.append(cleaned)

    if len(normalized) > 10:
        raise ValueError("A maximum of 10 unique tags is allowed.")

    return normalized


# ============== Prompt Models ==============

class PromptBase(BaseModel):
    """Shared prompt attributes used throughout the PromptLab API.

    Attributes:
        title: Human-readable title describing the prompt.
        content: The prompt's instructions or body text.
        description: Optional metadata giving additional context.
        collection_id: Optional identifier linking the prompt to a collection.

    Example:
        >>> PromptBase(
        ...     title="Summarize an article",
        ...     content="Summarize the provided text in 3 bullet points.",
        ...     description="General summarization guidance",
        ...     collection_id="collection-123",
        ... )
    """

    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    description: Optional[str] = Field(None, max_length=500)
    collection_id: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

    @field_validator("tags", mode="before")
    @classmethod
    def validate_tags(cls, value):
        return normalize_tags(value, allow_none=False)


class PromptCreate(PromptBase):
    """Model for creating prompts via the PromptLab API.

    Attributes:
        title: Human-readable title describing the prompt.
        content: The prompt's instructions or body text.
        description: Optional metadata giving additional context.
        collection_id: Optional identifier linking the prompt to a collection.

    Example:
        >>> PromptCreate(
        ...     title="Write a haiku",
        ...     content="Compose a haiku about autumn leaves.",
        ...     description="Creative writing exercise",
        ...     collection_id="seasonal-collection",
        ... )
    """


class PromptUpdate(PromptBase):
    """Model for fully updating existing prompts in PromptLab.

    Attributes:
        title: Human-readable title describing the prompt.
        content: The prompt's instructions or body text.
        description: Optional metadata giving additional context.
        collection_id: Optional identifier linking the prompt to a collection.

    Example:
        >>> PromptUpdate(
        ...     title="Rewrite in active voice",
        ...     content="Convert the supplied paragraph to active voice.",
        ...     description="Editing guidance",
        ...     collection_id="editing-tools",
        ... )
    """


class PromptPartialUpdate(BaseModel):
    """Model for partially updating prompt fields in the PromptLab API.

    Attributes:
        title: Optional new title describing the prompt.
        content: Optional new instructions or body text.
        description: Optional new metadata providing added context.
        collection_id: Optional new collection identifier to associate with the prompt.

    Example:
        >>> PromptPartialUpdate(
        ...     description="Updated to include tone guidance",
        ... )
    """

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = Field(None, max_length=500)
    collection_id: Optional[str] = None
    tags: Optional[List[str]] = None

    @field_validator("tags", mode="before")
    @classmethod
    def validate_tags(cls, value):
        return normalize_tags(value, allow_none=True)


class Prompt(PromptBase):
    """Complete prompt model returned by the PromptLab API.

    Attributes:
        title: Human-readable title describing the prompt.
        content: The prompt's instructions or body text.
        description: Optional metadata giving additional context.
        collection_id: Optional identifier linking the prompt to a collection.
        id: Unique identifier for the prompt.
        created_at: Timestamp indicating when the prompt was created.
        updated_at: Timestamp indicating the last modification time.

    Example:
        >>> Prompt(
        ...     title="Classify sentiment",
        ...     content="Label the supplied review as positive, neutral, or negative.",
        ...     description="Sentiment analysis prompt",
        ...     collection_id="nlp-basics",
        ... )
    """

    id: str = Field(default_factory=generate_id)
    created_at: datetime = Field(default_factory=get_current_time)
    updated_at: datetime = Field(default_factory=get_current_time)

    class Config:
        from_attributes = True


# ============== Collection Models ==============

class CollectionBase(BaseModel):
    """Base collection attributes shared across PromptLab operations.

    Attributes:
        name: Display name of the collection.
        description: Optional metadata describing the collection purpose.

    Example:
        >>> CollectionBase(
        ...     name="Productivity",
        ...     description="Prompts designed to improve focus and organization",
        ... )
    """

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class CollectionCreate(CollectionBase):
    """Model for creating collections via the PromptLab API.

    Attributes:
        name: Display name of the collection.
        description: Optional metadata describing the collection purpose.

    Example:
        >>> CollectionCreate(
        ...     name="Customer Support",
        ...     description="Prompts for handling customer inquiries",
        ... )
    """


class Collection(CollectionBase):
    """Collection model returned by the PromptLab API.

    Attributes:
        name: Display name of the collection.
        description: Optional metadata describing the collection purpose.
        id: Unique identifier for the collection.
        created_at: Timestamp indicating when the collection was created.

    Example:
        >>> Collection(
        ...     name="Education",
        ...     description="Teaching and tutoring prompts",
        ... )
    """

    id: str = Field(default_factory=generate_id)
    created_at: datetime = Field(default_factory=get_current_time)

    class Config:
        from_attributes = True


# ============== Response Models ==============

class PromptList(BaseModel):
    """Paginated response model for prompt listings in the PromptLab API.

    Attributes:
        prompts: The list of prompt resources for the current page.
        total: Total number of prompts available across all pages.

    Example:
        >>> PromptList(
        ...     prompts=[
        ...         Prompt(
        ...             title="Summarize",
        ...             content="Summarize the text.",
        ...         )
        ...     ],
        ...     total=1,
        ... )
    """

    prompts: List[Prompt]
    total: int


class CollectionList(BaseModel):
    """Paginated response model for collection listings in the PromptLab API.

    Attributes:
        collections: The list of collection resources for the current page.
        total: Total number of collections available across all pages.

    Example:
        >>> CollectionList(
        ...     collections=[
        ...         Collection(
        ...             name="Examples",
        ...             description="Sample prompts",
        ...         )
        ...     ],
        ...     total=1,
        ... )
    """

    collections: List[Collection]
    total: int


class HealthResponse(BaseModel):
    """Health check response model for the PromptLab API.

    Attributes:
        status: Current status string for the service.
        version: Semantic version or git hash describing the running build.

    Example:
        >>> HealthResponse(status="ok", version="1.0.0")
    """

    status: str
    version: str

