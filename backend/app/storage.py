"""In-memory storage for PromptLab

This module provides simple in-memory storage for prompts and collections.
In a production environment, this would be replaced with a database.
"""

from typing import Dict, List, Optional
from app.models import Prompt, Collection, PromptVersion


class Storage:
    """Provides in-memory persistence for prompts and collections.

    Example:
        >>> storage = Storage()
    """

    def __init__(self):
        """Initialize the in-memory dictionaries for prompts and collections.

        Args:
            None.

        Returns:
            None: The internal dictionaries are initialized in place.

        Example:
            >>> storage = Storage()
        """
        self._prompts: Dict[str, Prompt] = {}
        self._collections: Dict[str, Collection] = {}
        self._prompt_versions: Dict[str, List[PromptVersion]] = {}
    
    # ============== Prompt Operations ==============
    
    def create_prompt(self, prompt: Prompt) -> Prompt:
        """Store a prompt by its identifier.

        Args:
            prompt (Prompt): The prompt entity to persist.

        Returns:
            Prompt: The prompt that was stored.

        Example:
            >>> storage = Storage()
            >>> storage.create_prompt(Prompt(...))
            Prompt(...)
        """
        self._prompts[prompt.id] = prompt
        return prompt
    
    def get_prompt(self, prompt_id: str) -> Optional[Prompt]:
        """Retrieve a prompt by its identifier.

        Args:
            prompt_id (str): The unique identifier of the prompt to fetch.

        Returns:
            Optional[Prompt]: The matching prompt if it exists, otherwise ``None``.

        Example:
            >>> storage = Storage()
            >>> storage.create_prompt(Prompt(id="prompt-1", ...))
            >>> storage.get_prompt("prompt-1")
            Prompt(...)
        """
        return self._prompts.get(prompt_id)
    
    def get_all_prompts(self) -> List[Prompt]:
        """Return every prompt currently stored.

        Args:
            None.

        Returns:
            List[Prompt]: A list containing all prompts in storage.

        Example:
            >>> storage = Storage()
            >>> storage.create_prompt(Prompt(...))
            >>> storage.get_all_prompts()
            [Prompt(...)]
        """
        return list(self._prompts.values())
    
    # ============== Prompt Version Operations ==============
    
    def create_version(self, prompt_id: str, prompt: Prompt) -> PromptVersion:
        """Snapshot the current state of a prompt as a new version.
    
        Args:
            prompt_id (str): The identifier of the prompt being versioned.
            prompt (Prompt): The prompt whose data should be captured.
    
        Returns:
            PromptVersion: The newly created version record.
    
        Example:
            >>> storage = Storage()
            >>> prompt = storage.create_prompt(Prompt(...))
            >>> storage.create_version(prompt.id, prompt)
            PromptVersion(...)
        """
        versions = self._prompt_versions.setdefault(prompt_id, [])
        next_version_number = versions[-1].version_number + 1 if versions else 1
        version = PromptVersion(
            prompt_id=prompt_id,
            version_number=next_version_number,
            title=prompt.title,
            content=prompt.content,
            description=prompt.description,
            tags=list(prompt.tags),
        )
        versions.append(version)
        return version
    
    def get_versions(self, prompt_id: str) -> List[PromptVersion]:
        """Return every stored version for a prompt, ordered from newest to oldest.

        Args:
            prompt_id (str): The identifier of the prompt whose versions should be listed.

        Returns:
            List[PromptVersion]: A reverse-chronological list of prompt versions.

        Example:
            >>> storage = Storage()
            >>> storage.get_versions("prompt-1")
            [PromptVersion(...), ...]
        """
        versions = self._prompt_versions.get(prompt_id, [])
        return list(reversed(versions))
    
    def get_version(self, prompt_id: str, version_number: int) -> Optional[PromptVersion]:
        """Retrieve a specific version of a prompt by version number.

        Args:
            prompt_id (str): The identifier of the prompt that owns the version.
            version_number (int): The sequential version number to retrieve.

        Returns:
            Optional[PromptVersion]: The matching version if it exists, otherwise ``None``.

        Example:
            >>> storage = Storage()
            >>> storage.get_version("prompt-1", 1)
            PromptVersion(...)
        """
        versions = self._prompt_versions.get(prompt_id, [])
        for version in versions:
            if version.version_number == version_number:
                return version
        return None
    
    def update_prompt(self, prompt_id: str, prompt: Prompt) -> Optional[Prompt]:
        """Replace an existing prompt with a new value.

        Args:
            prompt_id (str): The identifier of the prompt to update.
            prompt (Prompt): The new prompt data to store.

        Returns:
            Optional[Prompt]: The updated prompt if the identifier exists, otherwise ``None``.

        Example:
            >>> storage = Storage()
            >>> storage.create_prompt(Prompt(id="prompt-1", ...))
            >>> storage.update_prompt("prompt-1", Prompt(id="prompt-1", ...))
            Prompt(...)
        """
        if prompt_id not in self._prompts:
            return None
        self._prompts[prompt_id] = prompt
        return prompt
    
    def delete_prompt(self, prompt_id: str) -> bool:
        """Remove a stored prompt.

        Args:
            prompt_id (str): The identifier of the prompt to delete.

        Returns:
            bool: ``True`` if the prompt was removed, ``False`` otherwise.

        Example:
            >>> storage = Storage()
            >>> storage.create_prompt(Prompt(id="prompt-1", ...))
            >>> storage.delete_prompt("prompt-1")
            True
        """
        if prompt_id in self._prompts:
            del self._prompts[prompt_id]
            self._prompt_versions.pop(prompt_id, None)
            return True
        return False
    
    # ============== Collection Operations ==============
    
    def create_collection(self, collection: Collection) -> Collection:
        """Store a collection by its identifier.

        Args:
            collection (Collection): The collection entity to persist.

        Returns:
            Collection: The collection that was stored.

        Example:
            >>> storage = Storage()
            >>> storage.create_collection(Collection(...))
            Collection(...)
        """
        self._collections[collection.id] = collection
        return collection
    
    def get_collection(self, collection_id: str) -> Optional[Collection]:
        """Retrieve a collection by its identifier.

        Args:
            collection_id (str): The unique identifier of the collection to fetch.

        Returns:
            Optional[Collection]: The matching collection if it exists, otherwise ``None``.

        Example:
            >>> storage = Storage()
            >>> storage.create_collection(Collection(id="collection-1", ...))
            >>> storage.get_collection("collection-1")
            Collection(...)
        """
        return self._collections.get(collection_id)
    
    def get_all_collections(self) -> List[Collection]:
        """Return every collection currently stored.

        Args:
            None.

        Returns:
            List[Collection]: A list containing all collections in storage.

        Example:
            >>> storage = Storage()
            >>> storage.create_collection(Collection(...))
            >>> storage.get_all_collections()
            [Collection(...)]
        """
        return list(self._collections.values())
    
    def delete_collection(self, collection_id: str) -> bool:
        """Remove a stored collection.

        Args:
            collection_id (str): The identifier of the collection to delete.

        Returns:
            bool: ``True`` if the collection was removed, ``False`` otherwise.

        Example:
            >>> storage = Storage()
            >>> storage.create_collection(Collection(id="collection-1", ...))
            >>> storage.delete_collection("collection-1")
            True
        """
        if collection_id in self._collections:
            del self._collections[collection_id]
            return True
        return False
    
    def get_prompts_by_collection(self, collection_id: str) -> List[Prompt]:
        """Return prompts that belong to a specific collection.

        Args:
            collection_id (str): The identifier of the collection whose prompts should be fetched.

        Returns:
            List[Prompt]: A list of prompts that reference the specified collection.

        Example:
            >>> storage = Storage()
            >>> storage.create_prompt(Prompt(id="prompt-1", collection_id="collection-1", ...))
            >>> storage.get_prompts_by_collection("collection-1")
            [Prompt(...)]
        """
        return [p for p in self._prompts.values() if p.collection_id == collection_id]
    
    # ============== Utility ==============
    
    def clear(self):
        """Remove all prompts and collections from storage.

        Args:
            None.

        Returns:
            None: All stored prompts and collections are deleted in place.

        Example:
            >>> storage = Storage()
            >>> storage.create_prompt(Prompt(...))
            >>> storage.clear()
        """
        self._prompts.clear()
        self._collections.clear()
        self._prompt_versions.clear()


# Global storage instance
storage = Storage()
