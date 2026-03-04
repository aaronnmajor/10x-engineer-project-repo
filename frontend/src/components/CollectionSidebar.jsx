import React, { useState, useEffect } from 'react';
import { getCollections } from '../services/api';
import '../styles/CollectionSidebar.css';

function CollectionSidebar({ onSelectCollection, selectedCollection }) {
  const [collections, setCollections] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isFormVisible, setFormVisible] = useState(false);
  const [newCollectionName, setNewCollectionName] = useState('');
  const [newCollectionDescription, setNewCollectionDescription] = useState('');

  useEffect(() => {
    fetchCollections();
  }, []);

  const fetchCollections = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getCollections();
      setCollections(data.collections);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectCollection = (collectionId) => {
    onSelectCollection(collectionId);
  };

  const handleDeleteCollection = (collectionId) => {
    if (window.confirm('Delete collection? Prompts will be unassigned, not deleted.')) {
      // Logic to delete collection
    }
  };

  const handleNewCollection = () => {
    // Logic to create a new collection
    setFormVisible(false);
  };

  return (
    <div className="collection-sidebar">
      <h2>Collections</h2>

      {loading && <div className="spinner">Loading...</div>}
      {error && <div className="error-message">{error}</div>}

      <ul className="collection-list">
        <li
          className={`collection-item ${!selectedCollection ? 'active' : ''}`}
          onClick={() => handleSelectCollection(null)}
        >
          All Prompts
        </li>
        {collections.map((collection) => (
          <li
            key={collection.id}
            className={`collection-item ${selectedCollection === collection.id ? 'active' : ''}`}
            onClick={() => handleSelectCollection(collection.id)}
          >
            {collection.name} <span>({collection.promptCount || 0})</span>
            <button onClick={(e) => { e.stopPropagation(); handleDeleteCollection(collection.id); }}>Delete</button>
          </li>
        ))}
      </ul>

      {isFormVisible ? (
        <div className="new-collection-form">
          <input
            type="text"
            placeholder="Collection Name"
            value={newCollectionName}
            onChange={e => setNewCollectionName(e.target.value)}
          />
          <textarea
            placeholder="Description"
            value={newCollectionDescription}
            onChange={e => setNewCollectionDescription(e.target.value)}
          ></textarea>
          <button onClick={handleNewCollection}>Save</button>
          <button onClick={() => setFormVisible(false)}>Cancel</button>
        </div>
      ) : (
        <button onClick={() => setFormVisible(true)} className="new-collection-button">New Collection</button>
      )}
    </div>
  );
}

export default CollectionSidebar;
