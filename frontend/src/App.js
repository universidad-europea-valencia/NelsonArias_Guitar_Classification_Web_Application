import React, { useState, useEffect } from 'react';
import './App.css';
import Header from './components/Header';
import ImageUploader from './components/ImageUploader';
import Results from './components/Results';

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [apiStatus, setApiStatus] = useState('checking');

  // Check API health on component mount
  useEffect(() => {
    checkAPIHealth();
  }, []);

  const checkAPIHealth = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/v1/health`);
      if (response.ok) {
        setApiStatus('healthy');
      } else {
        setApiStatus('unhealthy');
      }
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
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/v1/classify`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
      console.error('Classification error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <Header apiStatus={apiStatus} />
      <main className="container">
        <div className="content">
          <ImageUploader onUpload={handleImageUpload} loading={loading} />
          {error && <div className="error-message">{error}</div>}
          {result && <Results result={result} />}
        </div>
      </main>
    </div>
  );
}

export default App;
