import React, { useState, useEffect } from 'react';
import { getHealth } from './services/api';
import CollectionSidebar from './components/CollectionSidebar';
import PromptList from './components/PromptList';
import PromptForm from './components/PromptForm';
import './styles/App.css';

function App() {
  const [selectedCollection, setSelectedCollection] = useState(null);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingPrompt, setEditingPrompt] = useState(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [healthStatus, setHealthStatus] = useState(false);

  useEffect(() => {
    checkHealthStatus();
  }, []);

  const checkHealthStatus = async () => {
    try {
      const health = await getHealth();
      if (health.status === 'ok') {
        setHealthStatus(true);
      }
    } catch (error) {
      setHealthStatus(false);
    }
  };

  const handleCollectionSelect = (collectionId) => {
    setSelectedCollection(collectionId);
  };

  const handleNewPrompt = () => {
    setEditingPrompt(null);
    setIsFormOpen(true);
  };

  const handleEditPrompt = (prompt) => {
    setEditingPrompt(prompt);
    setIsFormOpen(true);
  };

  const handleDeletePrompt = () => {
    setRefreshTrigger((prev) => prev + 1);
  };

  const handleFormSave = () => {
    setRefreshTrigger((prev) => prev + 1);
    setIsFormOpen(false);
  };

  return (
    <div className="app-container">
      <CollectionSidebar
        onSelectCollection={handleCollectionSelect}
        selectedCollection={selectedCollection}
      />
      <div className="main-content-area">
        <header className="header">
          <h1>PromptLab</h1>
          <div className={`health-indicator ${healthStatus ? 'healthy' : 'unhealthy'}`}></div>
        </header>
        <PromptList
          selectedCollection={selectedCollection}
          refreshTrigger={refreshTrigger}
          onNewPrompt={handleNewPrompt}
          onEditPrompt={handleEditPrompt}
          onDeletePrompt={handleDeletePrompt}
        />
      </div>
      {isFormOpen && (
        <PromptForm
          isOpen={isFormOpen}
          onClose={() => setIsFormOpen(false)}
          onSave={handleFormSave}
          editingPrompt={editingPrompt}
        />
      )}
    </div>
  );
}

export default App;
