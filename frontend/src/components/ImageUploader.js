import React, { useState, useRef } from 'react';
import './ImageUploader.css';

function ImageUploader({ onUpload, loading, onModelChange, selectedModel }) {
  const [preview, setPreview] = useState(null);
  const [fileName, setFileName] = useState(null);
  const fileInputRef = useRef(null);
  const dragZoneRef = useRef(null);

  const MODELS = [
    { id: 'primary', label: 'Primary Model', description: 'Best Guitar Model' },
    { id: 'alternative', label: 'Alternative Model', description: 'Transfer Learning Model' },
    { id: 'ensemble', label: 'Ensemble Voting', description: 'Average of Both Models' },
  ];

  const handleFileSelect = (file) => {
    const maxSize = 4 * 1024 * 1024; // 4 MB
    
    if (!file) {
      return;
    }

    if (!file.type.startsWith('image/')) {
      alert('Please select a valid image file (JPG, PNG, GIF, BMP, WebP)');
      return;
    }

    if (file.size > maxSize) {
      alert(`File size exceeds 4 MB limit. Your file: ${(file.size / 1024 / 1024).toFixed(2)} MB`);
      return;
    }

    setFileName(file.name);

    const reader = new FileReader();
    reader.onload = (e) => {
      setPreview(e.target.result);
    };
    reader.onerror = () => {
      alert('Failed to read file');
    };
    reader.readAsDataURL(file);

    onUpload(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    dragZoneRef.current?.classList.add('drag-over');
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    dragZoneRef.current?.classList.remove('drag-over');
  };

  const handleDrop = (e) => {
    e.preventDefault();
    dragZoneRef.current?.classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    if (files && files[0]) {
      handleFileSelect(files[0]);
    }
  };

  const handleInputChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelect(e.target.files[0]);
    }
  };

  return (
    <div className="image-uploader">
      <div className="uploader-card">
        <h2>Upload Guitar Image</h2>

        {/* Model Selector */}
        <div className="model-selector">
          <label htmlFor="model-select">Select Classification Model:</label>
          <select
            id="model-select"
            value={selectedModel || 'primary'}
            onChange={(e) => onModelChange(e.target.value)}
            disabled={loading}
            className="model-dropdown"
          >
            {MODELS.map((model) => (
              <option key={model.id} value={model.id}>
                {model.label} - {model.description}
              </option>
            ))}
          </select>
        </div>

        <div
          ref={dragZoneRef}
          className="drag-zone"
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => !loading && fileInputRef.current?.click()}
          style={{ cursor: loading ? 'not-allowed' : 'pointer' }}
        >
          <div className="drag-content">
            <svg className="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="17 8 12 3 7 8"></polyline>
              <line x1="12" y1="3" x2="12" y2="15"></line>
            </svg>
            <p className="drag-text">
              {loading ? 'Processing...' : 'Drag and drop your guitar image here'}
            </p>
            <p className="drag-subtext">or click to select (Max 4 MB)</p>
          </div>
        </div>

        <input
          ref={fileInputRef}
          type="file"
          accept="image/jpeg,image/png,image/gif,image/bmp,image/webp"
          onChange={handleInputChange}
          disabled={loading}
          style={{ display: 'none' }}
        />

        {preview && (
          <div className="preview-container">
            <img src={preview} alt="Preview" className="preview-image" />
            <div className="preview-info">
              <p className="preview-text">{loading ? 'Classifying...' : 'Image ready for classification'}</p>
              <p className="preview-filename">{fileName}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default ImageUploader;
