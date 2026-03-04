import React, { useState, useEffect } from 'react';
import { getPrompts } from '../services/api';
import PromptCard from './PromptCard';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';
import '../styles/PromptList.css';

function PromptList({ selectedCollection, refreshTrigger, onNewPrompt, onEditPrompt, onDeletePrompt }) {
  const [prompts, setPrompts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');

  useEffect(() => {
    fetchPrompts();
  }, [selectedCollection, search, refreshTrigger]);

  // Improved fetch with error handler
  const fetchPrompts = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = { collection_id: selectedCollection, search };
      const data = await getPrompts(params);
      setPrompts(data.prompts);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchChange = (e) => {
    setSearch(e.target.value);
  };

  return (
    <div className="prompt-list-container">
      {/* Search Bar and New Prompt Button */}
      <div className="prompt-list-header">
        <input
          type="text"
          placeholder="Search prompts..."
          value={search}
          onChange={handleSearchChange}
          className="search-bar"
        />
        <button className="new-prompt-button" onClick={onNewPrompt}>
          New Prompt
        </button>
      </div>

      {/* Loading State */}
      {loading && <LoadingSpinner />}

      {/* Error State */}
      {error && <ErrorMessage message={error} onRetry={fetchPrompts} />}

      {/* Empty State */}
      {!loading && prompts.length === 0 && (
        <div className="empty-state">
          <span style={{ fontSize: '48px' }}>📝</span>
          <p>No prompts yet. Create your first prompt!</p>
          <button onClick={onNewPrompt}>Create your first prompt</button>
        </div>
      )}

      {/* Prompt List */}
      {!loading && !error && (
        <div className="prompt-grid">
          {prompts.map((prompt) => (
            <PromptCard
              key={prompt.id}
              prompt={prompt}
              onEdit={() => onEditPrompt(prompt)}
              onDelete={() => onDeletePrompt(prompt.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default PromptList;

