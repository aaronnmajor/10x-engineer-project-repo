import React from 'react';
import '../styles/PromptList.css';

function PromptCard({ prompt }) {
  const { id, title, content, tags, collection_id, created_at } = prompt;
  const truncatedContent = content.length > 100 ? content.substring(0, 100) + '...' : content;

  const handleEdit = () => {
    // Logic to open the edit form
  };

  const handleDelete = () => {
    if (window.confirm('Are you sure you want to delete this prompt?')) {
      // Logic to delete prompt
    }
  };

  return (
    <div className="prompt-card" onClick={handleEdit}>
      <h3>{title}</h3>
      <p>{truncatedContent}</p>
      <div className="tags">
        {tags.map((tag, index) => (
          <span key={index} className="tag">{tag}</span>
        ))}
      </div>
      <div className="card-footer">
        <span>{collection_id ? `Collection: ${collection_id}` : 'No Collection'}</span>
        <span>{new Date(created_at).toLocaleDateString()}</span>
      </div>
      <div className="card-actions">
        <button onClick={handleEdit}>Edit</button>
        <button onClick={(e) => { e.stopPropagation(); handleDelete(); }}>Delete</button>
      </div>
    </div>
  );
}

export default PromptCard;
