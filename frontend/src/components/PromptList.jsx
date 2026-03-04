import React, { useState, useEffect } from 'react';
import { getPrompts } from '../services/api';
import PromptCard from './PromptCard';
import '../styles/PromptList.css';

function PromptList({ selectedCollection }) {
  const [prompts, setPrompts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');

  useEffect(() => {
    fetchPrompts();
  }, [selectedCollection, search]);

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
      <div className="prompt-list-header">
        <input
          type="text"
          placeholder="Search prompts..."
          value={search}
          onChange={handleSearchChange}
          className="search-bar"
        />
        <button className="new-prompt-button">New Prompt</button>
      </div>

      {loading && <div className="spinner">Loading...</div>}
      {error && <div className="error-message">{error}</div>}
      {!loading && prompts.length === 0 && (
        <div className="empty-state">No prompts yet. Create your first prompt!</div>
      )}

      <div className="prompt-grid">
        {prompts.map((prompt) => (
          <PromptCard key={prompt.id} prompt={prompt} />
        ))}
      </div>
    </div>
  );
}

export default PromptList;
