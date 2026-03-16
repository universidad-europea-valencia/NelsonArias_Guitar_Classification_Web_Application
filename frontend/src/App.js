import React, { useState, useEffect } from 'react';
import './App.css';
import Header from './components/Header';
import ImageUploader from './components/ImageUploader';
import Results from './components/Results';
import { classificationAPI, handleAPIError } from './services/api';

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [apiStatus, setApiStatus] = useState('checking');
  const [selectedModel, setSelectedModel] = useState('primary');

  // Check API health on component mount and periodically
  useEffect(() => {
    checkAPIHealth();
    const healthCheckInterval = setInterval(checkAPIHealth, 30000); // Every 30 seconds
    return () => clearInterval(healthCheckInterval);
  }, []);

  const checkAPIHealth = async () => {
    try {
      const health = await classificationAPI.checkHealth();
      setApiStatus(health.ok ? 'healthy' : 'unavailable');
    } catch (error) {
      console.error('API health check failed:', error);
      setApiStatus('unavailable');
    }
  };

  const handleImageUpload = async (file) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      let classificationResult;

      // Call appropriate classification endpoint based on selected model
      switch (selectedModel) {
        case 'primary':
          classificationResult = await classificationAPI.classifyPrimary(file);
          break;
        case 'alternative':
          classificationResult = await classificationAPI.classifyAlternative(file);
          break;
        case 'ensemble':
          classificationResult = await classificationAPI.classifyEnsemble(file);
          break;
        default:
          classificationResult = await classificationAPI.classifyPrimary(file);
      }

      setResult(classificationResult);
    } catch (err) {
      const errorMessage = handleAPIError(err);
      setError(errorMessage);
      console.error('Classification error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleModelChange = (model) => {
    setSelectedModel(model);
    setResult(null);
    setError(null);
  };

  return (
    <div className="App">
      <Header apiStatus={apiStatus} />
      <main className="container">
        <div className="content">
          <ImageUploader
            onUpload={handleImageUpload}
            loading={loading}
            onModelChange={handleModelChange}
            selectedModel={selectedModel}
          />
          {error && (
            <div className="error-container">
              <div className="error-message">
                <svg className="error-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <circle cx="12" cy="12" r="10"></circle>
                  <line x1="12" y1="8" x2="12" y2="12"></line>
                  <line x1="12" y1="16" x2="12.01" y2="16"></line>
                </svg>
                <p>{error}</p>
              </div>
            </div>
          )}
          {result && <Results result={result} />}
        </div>
      </main>
    </div>
  );
}

export default App;
