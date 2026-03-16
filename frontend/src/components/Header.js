import React from 'react';
import './Header.css';

function Header({ apiStatus }) {
  const getStatusColor = () => {
    switch (apiStatus) {
      case 'healthy':
        return '#10b981';
      case 'unhealthy':
        return '#ef4444';
      case 'unavailable':
        return '#f97316';
      default:
        return '#f59e0b';
    }
  };

  const getStatusMessage = () => {
    switch (apiStatus) {
      case 'healthy':
        return 'API Ready';
      case 'unhealthy':
        return 'API Error';
      case 'unavailable':
        return 'Backend Unavailable';
      default:
        return 'Checking...';
    }
  };

  return (
    <header className="header">
      <div className="header-container">
        <div className="header-content">
          <div className="header-logo">
            <span className="logo-icon">🎸</span>
          </div>
          <div>
            <h1 className="header-title">Guitar Classification Platform</h1>
            <p className="header-subtitle">AI-powered image recognition system for guitar type classification</p>
          </div>
        </div>
        <div className="header-info">
          <div className={`api-status api-status-${apiStatus}`} style={{ '--status-color': getStatusColor() }}>
            <span className="status-indicator"></span>
            <span className="status-text">{getStatusMessage()}</span>
          </div>
          <p className="api-version">v1.0 - PHASE 3</p>
        </div>
      </div>
    </header>
  );
}

export default Header;
