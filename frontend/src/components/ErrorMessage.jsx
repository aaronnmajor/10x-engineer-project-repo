import React from 'react';
import '../styles/ErrorMessage.css';

function ErrorMessage({ message, onRetry }) {
  return (
    <div className="error-message-box">
      <p>{message}</p>
      {onRetry && <button onClick={onRetry} className="retry-button">Retry</button>}
    </div>
  );
}

export default ErrorMessage;
