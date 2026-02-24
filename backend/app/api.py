"""FastAPI routes for PromptLab"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Union

from app.models import (
    Prompt, PromptCreate, PromptUpdate, PromptPartialUpdate,
    Collection, CollectionCreate,
    PromptList, CollectionList, HealthResponse,
    PromptVersion, PromptVersionList,
    get_current_time
)
from app.storage import storage
from app.utils import (
    sort_prompts_by_date,
    filter_prompts_by_collection,
    filter_prompts_by_tags,
    search_prompts,
)
from app import __version__


app = FastAPI(
    title="PromptLab API",
    description="AI Prompt Engineering Platform",
    version=__version__
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== Health Check ==============

@app.get("/health", response_model=HealthResponse)
def health_check():
    """Check API health status and version metadata.

    Args:
        None.

    Returns:
        HealthResponse: Service status information and semantic version metadata.

    Raises:
        HTTPException: 500 if the health check encounters an unexpected server error.

    Example:
        >>> curl -X GET "http://localhost:8000/health"
    """
    return HealthResponse(status="healthy", version=__version__)


# ============== Prompt Endpoints ==============

@app.get("/prompts", response_model=Union[PromptList, List[Prompt]])
def list_prompts(
    collection_id: Optional[str] = None,
    search: Optional[str] = None,
    tags: Optional[str] = None,
):
    """Retrieve prompts with optional collection and keyword filters.

    Args:
        collection_id (Optional[str]): Identifier of the collection used to limit the result set.
        search (Optional[str]): Case-insensitive term applied to prompt titles, descriptions, and content.
        tags (Optional[str]): Comma-separated tags that prompts must all contain.

    Returns:
        PromptList: Sorted prompts and the total count after filtering.

    Raises:
        HTTPException: 500 if prompt retrieval fails unexpectedly.

    Example:
        >>> curl -G "http://localhost:8000/prompts" --data-urlencode "collection_id=abc123" --data-urlencode "search=chatbot"
    """
    prompts = storage.get_all_prompts()
    tags_filter_applied = False
    
    # Filter by collection if specified
    if collection_id:
        prompts = filter_prompts_by_collection(prompts, collection_id)
    
    # Search if query provided
    if search:
        prompts = search_prompts(prompts, search)

    if tags:
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        if tag_list:
            prompts = filter_prompts_by_tags(prompts, tag_list)
            tags_filter_applied = True
    
    # Sort by date (newest first)
    prompts = sort_prompts_by_date(prompts, descending=True)

    if tags_filter_applied:
        return prompts
    
    return PromptList(prompts=prompts, total=len(prompts))


@app.get("/prompts/{prompt_id}", response_model=Prompt)
def get_prompt(prompt_id: str):
    """Fetch a single prompt by its unique identifier.

    Args:
        prompt_id (str): Unique identifier of the prompt to retrieve.

    Returns:
        Prompt: Prompt resource that matches the provided identifier.

    Raises:
        HTTPException: 404 if the prompt does not exist.

    Example:
        >>> curl -X GET "http://localhost:8000/prompts/123e4567"
    """
    prompt = storage.get_prompt(prompt_id)
    # Check if prompt is None
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt
    

@app.post("/prompts", response_model=Prompt, status_code=201)
def create_prompt(prompt_data: PromptCreate):
    """Create a new prompt resource.

    Args:
        prompt_data (PromptCreate): Validated data describing the prompt to persist.

    Returns:
        Prompt: Newly created prompt instance.

    Raises:
        HTTPException: 400 if the supplied collection_id does not reference an existing collection.

    Example:
        >>> curl -X POST "http://localhost:8000/prompts" -H "Content-Type: application/json" -d '{"title":"Greeting","content":"Hello"}'
    """
    # Validate collection exists if provided
    if prompt_data.collection_id:
        collection = storage.get_collection(prompt_data.collection_id)
        if not collection:
            raise HTTPException(status_code=400, detail="Collection not found")
    
    prompt = Prompt(**prompt_data.model_dump())
    saved_prompt = storage.create_prompt(prompt)
    storage.create_version(saved_prompt.id, saved_prompt)
    return saved_prompt


@app.put("/prompts/{prompt_id}", response_model=Prompt)
def update_prompt(prompt_id: str, prompt_data: PromptUpdate):
    """Replace an existing prompt with updated field values.

    Args:
        prompt_id (str): Unique identifier of the prompt to update.
        prompt_data (PromptUpdate): Replacement values for the prompt.

    Returns:
        Prompt: Updated prompt persisted in storage.

    Raises:
        HTTPException: 404 if the prompt does not exist.
        HTTPException: 400 if the supplied collection_id does not reference an existing collection.

    Example:
        >>> curl -X PUT "http://localhost:8000/prompts/123e4567" -H "Content-Type: application/json" -d '{"title":"New Title","content":"Updated"}'
    """
    existing = storage.get_prompt(prompt_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    # Validate collection if provided
    if prompt_data.collection_id:
        collection = storage.get_collection(prompt_data.collection_id)
        if not collection:
            raise HTTPException(status_code=400, detail="Collection not found")

    # Build the updated prompt preserving non-updated fields
    updated_prompt = Prompt(
        id=existing.id,
        title=prompt_data.title if prompt_data.title is not None else existing.title,
        content=prompt_data.content if prompt_data.content is not None else existing.content,
        description=prompt_data.description if prompt_data.description is not None else existing.description,
        collection_id=prompt_data.collection_id if prompt_data.collection_id is not None else existing.collection_id,
        tags=prompt_data.tags if prompt_data.tags is not None else existing.tags,
        created_at=existing.created_at,
        updated_at=get_current_time()  # Correctly update the timestamp
    )

    saved_prompt = storage.update_prompt(prompt_id, updated_prompt)
    if not saved_prompt:
        raise HTTPException(status_code=500, detail="Failed to update prompt")

    storage.create_version(prompt_id, saved_prompt)
    return saved_prompt


# Added support for partial updates
@app.patch("/prompts/{prompt_id}", response_model=Prompt)
def patch_prompt(prompt_id: str, prompt_data: PromptPartialUpdate):
    """Partially update specific fields of a prompt.

    Args:
        prompt_id (str): Unique identifier of the prompt to update.
        prompt_data (PromptPartialUpdate): Subset of fields to modify.

    Returns:
        Prompt: Prompt instance reflecting the partial update.

    Raises:
        HTTPException: 404 if the prompt does not exist.

    Example:
        >>> curl -X PATCH "http://localhost:8000/prompts/123e4567" -H "Content-Type: application/json" -d '{"description":"Clarified use case"}'
    """
    existing = storage.get_prompt(prompt_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Prompt not found")

    # Build the updated prompt preserving non-updated fields
    updated_prompt = Prompt(
        id=existing.id,
        title=prompt_data.title if prompt_data.title is not None else existing.title,
        content=prompt_data.content if prompt_data.content is not None else existing.content,
        description=prompt_data.description if prompt_data.description is not None else existing.description,
        collection_id=prompt_data.collection_id if prompt_data.collection_id is not None else existing.collection_id,
        tags=prompt_data.tags if prompt_data.tags is not None else existing.tags,
        created_at=existing.created_at,
        updated_at=get_current_time()  # Correctly update the timestamp
    )

    saved_prompt = storage.update_prompt(prompt_id, updated_prompt)
    if not saved_prompt:
        raise HTTPException(status_code=500, detail="Failed to update prompt")

    storage.create_version(prompt_id, saved_prompt)
    return saved_prompt



@app.delete("/prompts/{prompt_id}", status_code=204)
def delete_prompt(prompt_id: str):
    """Delete a prompt by its identifier.

    Args:
        prompt_id (str): Unique identifier of the prompt to delete.

    Returns:
        None: The response body is empty when deletion succeeds.

    Raises:
        HTTPException: 404 if the prompt does not exist.

    Example:
        >>> curl -X DELETE "http://localhost:8000/prompts/123e4567"
    """
    if not storage.delete_prompt(prompt_id):
        raise HTTPException(status_code=404, detail="Prompt not found")
    return None


# ============== Prompt Version Endpoints ==============

@app.get("/prompts/{prompt_id}/versions", response_model=PromptVersionList)
def list_prompt_versions(prompt_id: str, order: str = "desc"):
    """Return the historical versions for a prompt with optional ordering."""
    prompt = storage.get_prompt(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    if order not in {"asc", "desc"}:
        raise HTTPException(
            status_code=400,
            detail="order parameter must be either 'asc' or 'desc'",
        )

    versions_desc = storage.get_versions(prompt_id)
    versions = versions_desc if order == "desc" else list(reversed(versions_desc))
    return PromptVersionList(versions=versions, total=len(versions))


@app.get("/prompts/{prompt_id}/versions/{version_number}", response_model=PromptVersion)
def get_prompt_version(prompt_id: str, version_number: int):
    """Fetch a specific prompt version snapshot."""
    prompt = storage.get_prompt(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    version = storage.get_version(prompt_id, version_number)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    return version


@app.post("/prompts/{prompt_id}/versions/{version_number}/revert", response_model=Prompt)
def revert_prompt_version(prompt_id: str, version_number: int):
    """Revert a prompt to a historical version, creating a new snapshot."""
    prompt = storage.get_prompt(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    version = storage.get_version(prompt_id, version_number)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")

    reverted_prompt = Prompt(
        id=prompt.id,
        title=version.title,
        content=version.content,
        description=version.description,
        collection_id=prompt.collection_id,
        tags=list(version.tags),
        created_at=prompt.created_at,
        updated_at=get_current_time(),
    )

    saved_prompt = storage.update_prompt(prompt_id, reverted_prompt)
    if not saved_prompt:
        raise HTTPException(status_code=500, detail="Failed to revert prompt")

    storage.create_version(prompt_id, saved_prompt)
    return saved_prompt


# ============== Collection Endpoints ==============
@app.get("/collections", response_model=CollectionList)
def list_collections():
    """List all prompt collections.

    Args:
        None.

    Returns:
        CollectionList: All collections and their total count.

    Raises:
        HTTPException: 500 if collection retrieval fails unexpectedly.

    Example:
        >>> curl -X GET "http://localhost:8000/collections"
    """
    collections = storage.get_all_collections()
    return CollectionList(collections=collections, total=len(collections))


@app.get("/collections/{collection_id}", response_model=Collection)
def get_collection(collection_id: str):
    """Retrieve a collection by its identifier.

    Args:
        collection_id (str): Unique identifier of the collection to fetch.

    Returns:
        Collection: Resource that matches the provided identifier.

    Raises:
        HTTPException: 404 if the collection does not exist.

    Example:
        >>> curl -X GET "http://localhost:8000/collections/abc123"
    """
    collection = storage.get_collection(collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    return collection


@app.post("/collections", response_model=Collection, status_code=201)
def create_collection(collection_data: CollectionCreate):
    """Create a new prompt collection.

    Args:
        collection_data (CollectionCreate): Validated data for the collection to persist.

    Returns:
        Collection: Newly created collection.

    Raises:
        HTTPException: 500 if the collection cannot be persisted due to an unexpected error.

    Example:
        >>> curl -X POST "http://localhost:8000/collections" -H "Content-Type: application/json" -d '{"name":"Productivity"}'
    """
    collection = Collection(**collection_data.model_dump())
    return storage.create_collection(collection)


@app.delete("/collections/{collection_id}", status_code=204)
def delete_collection(collection_id: str):
    """Delete a collection and disassociate its prompts.

    Args:
        collection_id (str): Unique identifier of the collection to delete.

    Returns:
        None: The response body is empty when deletion succeeds.

    Raises:
        HTTPException: 404 if the collection does not exist.

    Example:
        >>> curl -X DELETE "http://localhost:8000/collections/abc123"
    """
    # Retrieve all prompts in the collection
    associated_prompts = [prompt for prompt in storage.get_all_prompts() if prompt.collection_id == collection_id]
    
    # Update each prompt's collection_id to None
    for prompt in associated_prompts:
        updated_prompt = prompt.copy(update={"collection_id": None})
        storage.update_prompt(prompt.id, updated_prompt)
    
    # Proceed with deleting the collection
    if not storage.delete_collection(collection_id):
        raise HTTPException(status_code=404, detail="Collection not found")
    
    return None

