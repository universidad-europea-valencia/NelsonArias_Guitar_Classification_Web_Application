import React, { useState } from 'react';
import './Results.css';

function Results({ result }) {
  const [showDetails, setShowDetails] = useState(false);

  if (!result) return null;

  const confidencePercentage = (result.confidence * 100).toFixed(2);
  const guitarType = result.predicted_class.replace(/_/g, ' ');
  const processingTime = result.processing_time_ms.toFixed(2);

  // Determine confidence level
  const getConfidenceLevel = (confidence) => {
    if (confidence >= 0.9) return 'Very High';
    if (confidence >= 0.8) return 'High';
    if (confidence >= 0.7) return 'Good';
    if (confidence >= 0.5) return 'Moderate';
    return 'Low';
  };

  // Determine confidence color
  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.9) return '#10b981';
    if (confidence >= 0.8) return '#3b82f6';
    if (confidence >= 0.7) return '#f59e0b';
    if (confidence >= 0.5) return '#f97316';
    return '#ef4444';
  };

  // Get sorted probabilities for chart
  const sortedProbabilities = result.class_probabilities
    ? Object.entries(result.class_probabilities)
        .map(([className, probability]) => ({
          name: className.replace(/_/g, ' '),
          value: probability,
          percentage: (probability * 100).toFixed(1),
        }))
        .sort((a, b) => b.value - a.value)
    : [];

  return (
    <div className="results">
      <div className="results-card">
        <div className="result-header">
          <h2>Classification Result</h2>
          <button
            className="toggle-details-btn"
            onClick={() => setShowDetails(!showDetails)}
          >
            {showDetails ? 'Hide Details' : 'Show Details'}
          </button>
        </div>

        {/* Main Result Display */}
        <div className="result-main">
          <div className="guitar-class">
            <h3 className="guitar-name">{guitarType}</h3>
            
            {/* Confidence Gauge */}
            <div className="confidence-section">
              <div className="confidence-display">
                <div className="confidence-circle">
                  <div className="confidence-value">{confidencePercentage}%</div>
                </div>
              </div>
              <div className="confidence-info">
                <p className="confidence-level">
                  Confidence: <span className="confidence-badge" style={{ backgroundColor: getConfidenceColor(result.confidence) }}>
                    {getConfidenceLevel(result.confidence)}
                  </span>
                </p>
                <div
                  className="confidence-bar"
                  style={{
                    '--confidence-value': result.confidence,
                    '--confidence-color': getConfidenceColor(result.confidence),
                  }}
                >
                  <div className="confidence-fill"></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Class Probabilities Distribution */}
        {result.class_probabilities && (
          <div className="probabilities-section">
            <h4>Probability Distribution</h4>
            <div className="probabilities-chart">
              {sortedProbabilities.map((prob, index) => (
                <div key={prob.name} className="probability-bar-item">
                  <div className="probability-rank">{index + 1}</div>
                  <span className="probability-class-name">{prob.name}</span>
                  <div className="probability-bar-wrapper">
                    <div
                      className="probability-bar-fill"
                      style={{
                        width: `${prob.value * 100}%`,
                        backgroundColor: getConfidenceColor(prob.value),
                      }}
                    >
                      <span className="probability-percentage">{prob.percentage}%</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Details Section */}
        {showDetails && (
          <div className="details-section">
            <h4>Detailed Information</h4>
            <div className="details-grid">
              <div className="detail-item">
                <span className="detail-label">Model Used:</span>
                <span className="detail-value">{result.model_used}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Processing Time:</span>
                <span className="detail-value">{processingTime}ms</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Timestamp:</span>
                <span className="detail-value">{new Date().toLocaleTimeString()}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">API Response:</span>
                <span className="detail-value">Success (200)</span>
              </div>
            </div>

            {/* Raw JSON (optional) */}
            <details className="json-details">
              <summary>Raw Response JSON</summary>
              <pre>{JSON.stringify(result, null, 2)}</pre>
            </details>
          </div>
        )}

        {/* Footer */}
        <div className="result-footer">
          <p className="result-timestamp">
            Classified at {new Date().toLocaleTimeString()}
          </p>
        </div>
      </div>
    </div>
  );
}

export default Results;
