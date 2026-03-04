import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';
import { getCollections, createPrompt, updatePrompt } from '../services/api';
import '../styles/PromptForm.css';

function PromptForm({ isOpen, onClose, onSave, editingPrompt }) {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [description, setDescription] = useState('');
  const [collectionId, setCollectionId] = useState('');
  const [tags, setTags] = useState([]);
  const [collections, setCollections] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCollections = async () => {
      try {
        const data = await getCollections();
        setCollections(data.collections);
      } catch (error) {
        setError(error.message);
      }
    };

    fetchCollections();
  }, []);

  useEffect(() => {
    if (editingPrompt) {
      setTitle(editingPrompt.title);
      setContent(editingPrompt.content);
      setDescription(editingPrompt.description || '');
      setCollectionId(editingPrompt.collection_id || '');
      setTags(editingPrompt.tags || []);
    }
  }, [editingPrompt]);

  const handleSave = async () => {
    setLoading(true);
    setError(null);
    try {
      const promptData = { title, content, description, collection_id: collectionId, tags };
      if (editingPrompt) {
        await updatePrompt(editingPrompt.id, promptData);
      } else {
        await createPrompt(promptData);
      }
      onSave();
      onClose();
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleTagAdd = (e) => {
    if (e.key === 'Enter' && e.target.value.trim() !== '') {
      const newTag = e.target.value.trim().toLowerCase();
      if (!tags.includes(newTag) && tags.length < 10) {
        setTags(prevTags => [...prevTags, newTag]);
      }
      e.target.value = '';
    }
  };

  const handleTagRemove = (tag) => {
    setTags(prevTags => prevTags.filter(t => t !== tag));
  };

  if (!isOpen) return null;

  return ReactDOM.createPortal(
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <h2>{editingPrompt ? 'Edit Prompt' : 'New Prompt'}</h2>
        {error && <div className="error-message">{error}</div>}

        <div className="form-group">
          <label>Title <span>({title.length}/200)</span></label>
          <input
            type="text"
            value={title}
            onChange={e => setTitle(e.target.value)}
            maxLength="200"
            required
          />
        </div>

        <div className="form-group">
          <label>Content <span>(required)</span></label>
          <textarea
            value={content}
            onChange={e => setContent(e.target.value)}
            rows="6"
            required
          />
        </div>

        <div className="form-group">
          <label>Description <span>({description.length}/500)</span></label>
          <textarea
            value={description}
            onChange={e => setDescription(e.target.value)}
            maxLength="500"
          />
        </div>

        <div className="form-group">
          <label>Collection</label>
          <select value={collectionId} onChange={e => setCollectionId(e.target.value)}>
            <option value="">None</option>
            {collections.map(collection => (
              <option key={collection.id} value={collection.id}>{collection.name}</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label>Tags</label>
          <div className="tags-input-container">
            <input type="text" onKeyDown={handleTagAdd} placeholder="Add a tag and press Enter" />
            <div className="tags-display">
              {tags.map((tag, index) => (
                <span key={index} className="tag-chip">
                  {tag} <button type="button" onClick={() => handleTagRemove(tag)}>&times;</button>
                </span>
              ))}
            </div>
          </div>
        </div>

        <div className="form-actions">
          <button onClick={onClose} className="cancel-button">Cancel</button>
          <button onClick={handleSave} className="save-button" disabled={!title || !content || loading}>
            {loading ? 'Saving...' : 'Save'}
          </button>
        </div>
      </div>
    </div>,
    document.body
  );
}

export default PromptForm;
