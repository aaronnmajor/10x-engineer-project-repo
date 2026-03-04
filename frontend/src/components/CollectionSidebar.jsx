import React, { useState, useEffect } from 'react';
import { getCollections, createCollection, deleteCollection } from '../services/api';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';
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

  const handleDeleteCollection = async (collectionId) => {
    if (window.confirm('Delete collection? Prompts will be unassigned, not deleted.')) {
      try {
        await deleteCollection(collectionId);
        fetchCollections();
      } catch (error) {
        console.error('Error deleting collection:', error);
      }
    }
  };

  const handleNewCollection = async () => {
    try {
      await createCollection({
        name: newCollectionName,
        description: newCollectionDescription,
      });
      fetchCollections();
    setFormVisible(false);
    } catch (error) {
      console.error('Error creating collection:', error);
    }
  };

  return (
    <div className="collection-sidebar">
      <h2>Collections</h2>

      {/* Loading Spinner */}
      {loading && <LoadingSpinner />}

      {/* Error Message */}
      {error && <ErrorMessage message={error} onRetry={fetchCollections} />}

      {/* Empty State for Collections */}
      {!loading && collections.length === 0 && (
        <div className="empty-state">
          <p>No collections yet. Create one to organize your prompts.</p>
        </div>
      )}

      {/* Collection List */}
      <ul className="collection-list">
        {/* All Prompts Item */}
        <li
          className={`collection-item ${!selectedCollection ? 'active' : ''}`}
          onClick={() => handleSelectCollection(null)}
        >
          All Prompts
        </li>

        {/* Collection Items */}
        {collections.map((collection) => (
          <li
            key={collection.id}
            className={`collection-item ${selectedCollection === collection.id ? 'active' : ''}`}
            onClick={() => handleSelectCollection(collection.id)}
          >
            {collection.name}
            <button onClick={(e) => { e.stopPropagation(); handleDeleteCollection(collection.id); }}>Delete</button>
          </li>
        ))}
      </ul>

      {/* New Collection Button/Form */}
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

