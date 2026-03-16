import React from 'react';
import './Results.css';

function Results({ result }) {
  if (!result) return null;

  const confidencePercentage = (result.confidence * 100).toFixed(2);
  const guitarType = result.predicted_class.replace(/_/g, ' ');

  return (
    <div className="results">
      <div className="results-card">
        <h2>Classification Result</h2>
        
        <div className="result-main">
          <div className="guitar-class">
            <h3>{guitarType}</h3>
            <div className="confidence-bar">
              <div
                className="confidence-fill"
                style={{ width: `${result.confidence * 100}%` }}
              ></div>
            </div>
            <p className="confidence-text">Confidence: {confidencePercentage}%</p>
          </div>
        </div>

        {result.class_probabilities && (
          <div className="probabilities">
            <h4>Class Probabilities</h4>
            <div className="probability-list">
              {Object.entries(result.class_probabilities).map(([className, probability]) => (
                <div key={className} className="probability-item">
                  <span className="class-name">{className.replace(/_/g, ' ')}</span>
                  <div className="probability-bar-small">
                    <div
                      className="probability-fill"
                      style={{ width: `${probability * 100}%` }}
                    ></div>
                  </div>
                  <span className="probability-value">{(probability * 100).toFixed(1)}%</span>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="result-metadata">
          <div className="metadata-item">
            <span className="metadata-label">Model Used:</span>
            <span className="metadata-value">{result.model_used}</span>
          </div>
          <div className="metadata-item">
            <span className="metadata-label">Processing Time:</span>
            <span className="metadata-value">{result.processing_time_ms.toFixed(2)}ms</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Results;
