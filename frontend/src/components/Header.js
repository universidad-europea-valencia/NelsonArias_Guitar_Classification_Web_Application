import React from 'react';
import './Header.css';

function Header({ apiStatus }) {
  return (
    <header className="header">
      <div className="header-container">
        <div className="header-content">
          <h1 className="header-title">🎸 Guitar Classification Platform</h1>
          <p className="header-subtitle">Classify guitars using AI-powered image recognition</p>
        </div>
        <div className={`api-status ${apiStatus}`}>
          <span className="status-indicator"></span>
          <span className="status-text">
            {apiStatus === 'healthy' ? 'API Ready' : apiStatus === 'unhealthy' ? 'API Error' : 'Checking...'}
          </span>
        </div>
      </div>
    </header>
  );
}

export default Header;
