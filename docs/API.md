# REST API Documentation

**Guitar Classification Platform - API Reference**  
**Version:** 1.0.0  
**Base URL:** `http://localhost:8000/api/v1`

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Endpoints](#endpoints)
4. [Request/Response Formats](#requestresponse-formats)
5. [Error Handling](#error-handling)
6. [Examples](#examples)

---

## Overview

The REST API provides endpoints for:
- **Health checks** - System status monitoring
- **Classification** - Single image classification
- **Model information** - Metadata about available models
- **Alternative models** - Using different prediction engines
- **Ensemble predictions** - Combining multiple models

### Base URL
```
http://localhost:8000/api/v1
```

### API Documentation (Interactive)
```
http://localhost:8000/docs
```

### Key Features
- ✅ RESTful design with standard HTTP methods
- ✅ JSON request/response format
- ✅ Comprehensive error responses
- ✅ Response time tracking
- ✅ Model metadata in responses

---

## Authentication

Currently, the API requires **no authentication**. All endpoints are publicly accessible.

*Future versions may add API keys or token-based authentication.*

---

## Endpoints

### 1. Health Check

**Check API server status and health.**

```
GET /health
```

#### Response (200 OK)
```json
{
  "status": "healthy",
  "timestamp": "2026-03-17T10:30:45.123Z",
  "version": "1.0.0"
}
```

#### Example
```bash
curl http://localhost:8000/api/v1/health
```

---

### 2. Classify Image (Primary Model)

**Classify a single guitar image using the primary model.**

```
POST /classify
```

#### Request

**Content-Type:** `multipart/form-data`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | File | Yes | Guitar image file (PNG, JPEG, WebP, GIF, BMP) |

**Constraints:**
- Max file size: 4 MB
- Supported formats: PNG, JPEG, WebP, GIF, BMP
- Recommended size: 224×224 or larger

#### Response (200 OK)

```json
{
  "predicted_class": "Guitarra_Electrica",
  "confidence": 0.9467,
  "processing_time_ms": 156.23,
  "all_probabilities": {
    "Guitarra_Electrica": 0.9467,
    "Guitarra_Acustica": 0.0312,
    "Guitarra_Electroacustica": 0.0156,
    "Bajo_Electrico": 0.0065
  },
  "model_used": "best_guitar_model.keras"
}
```

#### Error Responses

**400 Bad Request** - Invalid file or format
```json
{
  "detail": "Invalid image format or corrupted file"
}
```

**422 Unprocessable Entity** - Missing file parameter
```json
{
  "detail": [
    {
      "loc": ["body", "file"],
      "msg": "Field required",
      "type": "missing"
    }
  ]
}
```

**500 Internal Server Error** - Model inference failed
```json
{
  "detail": "Model inference failed: [error details]"
}
```

#### Example

```bash
# Using curl
curl -X POST "http://localhost:8000/api/v1/classify" \
  -F "file=@guitar_image.png"

# Using Python requests
import requests

with open('guitar_image.png', 'rb') as f:
    files = {'file': f}
    response = requests.post(
        'http://localhost:8000/api/v1/classify',
        files=files
    )
    print(response.json())
```

---

### 3. Classify Image (Alternative Model)

**Classify a guitar image using the alternative model.**

```
POST /classify-alternative
```

#### Request

Same as `/classify` endpoint

#### Response

Same schema as `/classify`, but with different model predictions

```json
{
  "predicted_class": "Guitarra_Acustica",
  "confidence": 0.8745,
  "processing_time_ms": 198.45,
  "all_probabilities": { /* ... */ },
  "model_used": "best_transfer_model.keras"
}
```

#### Example

```bash
curl -X POST "http://localhost:8000/api/v1/classify-alternative" \
  -F "file=@guitar_image.png"
```

---

### 4. Ensemble Classification

**Classify image using both models and average probabilities.**

```
POST /classify-ensemble
```

#### Request

Same as `/classify` endpoint

#### Response

```json
{
  "predicted_class": "Guitarra_Electrica",
  "confidence": 0.9106,
  "processing_time_ms": 325.67,
  "ensemble_method": "probability_averaging",
  "all_probabilities": {
    "Guitarra_Electrica": 0.9106,
    "Guitarra_Acustica": 0.0351,
    "Guitarra_Electroacustica": 0.0398,
    "Bajo_Electrico": 0.0145
  },
  "individual_predictions": {
    "best_guitar_model.keras": {
      "class": "Guitarra_Electrica",
      "confidence": 0.9467
    },
    "best_transfer_model.keras": {
      "class": "Guitarra_Electrica",
      "confidence": 0.8745
    }
  }
}
```

#### Example

```bash
curl -X POST "http://localhost:8000/api/v1/classify-ensemble" \
  -F "file=@guitar_image.png"
```

---

## Request/Response Formats

### Content Types

**Request:**
- `multipart/form-data` - For file uploads (classification endpoints)
- `application/json` - For future query parameters

**Response:**
- `application/json` - All responses are JSON

### Class Labels

The API returns predictions for 4 guitar classes:

| Label | English | Description |
|-------|---------|-------------|
| `Bajo_Electrico` | Electric Bass | 4-6 string bass guitar |
| `Guitarra_Acustica` | Acoustic Guitar | Unplugged acoustic guitar |
| `Guitarra_Electrica` | Electric Guitar | Plugged electric guitar |
| `Guitarra_Electroacustica` | Electroacoustic | Acoustic guitar with pickup |

### Confidence Scores

- **Range:** 0.0 to 1.0 (or 0-100%)
- **Interpretation:** 0.95 = 95% confidence
- **Sum of all classes:** Always equals 1.0
- **Model trained accuracy:** ~85-86% on validation set

### Processing Time

- **Included in response** as `processing_time_ms`
- **Typical range:** 150-250ms (CPU-based)
- **Includes:** Image loading, preprocessing, inference
- **Excludes:** Network latency, request parsing

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | When |
|------|---------|------|
| **200** | Success | Prediction successful |
| **400** | Bad Request | Invalid file or format |
| **422** | Validation Error | Missing/invalid parameters |
| **500** | Server Error | Model/processing failure |

### Error Response Format

```json
{
  "detail": "Human-readable error message"
}
```

Or for validation errors:

```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "Error description",
      "type": "error_type"
    }
  ]
}
```

### Common Errors

**Invalid Image Format**
```json
{
  "detail": "Invalid image format or corrupted file"
}
```

**File Too Large**
```json
{
  "detail": "File size exceeds maximum limit of 4 MB"
}
```

**Missing File**
```json
{
  "detail": "File parameter is required"
}
```

**Model Not Available**
```json
{
  "detail": "Model not found or failed to load"
}
```

---

## Examples

### Example 1: Simple Classification

```bash
#!/bin/bash

# Classify a guitar image
curl -X POST "http://localhost:8000/api/v1/classify" \
  -F "file=@acoustic_guitar.jpg" \
  -H "Accept: application/json"

# Response:
# {
#   "predicted_class": "Guitarra_Acustica",
#   "confidence": 0.8923,
#   "processing_time_ms": 145.67,
#   ...
# }
```

### Example 2: Python Integration

```python
import requests
import json

def classify_guitar(image_path, model='primary'):
    """Classify a guitar image."""
    
    url = "http://localhost:8000/api/v1/classify"
    
    if model == 'alternative':
        url = "http://localhost:8000/api/v1/classify-alternative"
    elif model == 'ensemble':
        url = "http://localhost:8000/api/v1/classify-ensemble"
    
    with open(image_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, files=files)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Prediction: {result['predicted_class']}")
        print(f"Confidence: {result['confidence']:.2%}")
        print(f"Time: {result['processing_time_ms']:.2f}ms")
        return result
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
        return None

# Usage
result = classify_guitar('my_guitar.png', model='ensemble')
```

### Example 3: JavaScript/Fetch

```javascript
async function classifyGuitar(file, model = 'primary') {
  const endpoint = {
    'primary': '/api/v1/classify',
    'alternative': '/api/v1/classify-alternative',
    'ensemble': '/api/v1/classify-ensemble'
  }[model];

  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const result = await response.json();
    console.log(`Predicted: ${result.predicted_class}`);
    console.log(`Confidence: ${(result.confidence * 100).toFixed(2)}%`);
    console.log(`Processing time: ${result.processing_time_ms.toFixed(2)}ms`);

    return result;
  } catch (error) {
    console.error('Classification failed:', error);
    return null;
  }
}

// Usage
const fileInput = document.querySelector('input[type="file"]');
const file = fileInput.files[0];
classifyGuitar(file, 'ensemble');
```

### Example 4: Batch Processing

```python
import os
import requests
from pathlib import Path

def batch_classify(image_directory, model='primary'):
    """Classify all images in a directory."""
    
    url = f"http://localhost:8000/api/v1/classify"
    if model == 'ensemble':
        url = url.replace('/classify', '/classify-ensemble')
    
    results = []
    
    for image_file in Path(image_directory).glob('*.jpg'):
        print(f"Processing: {image_file.name}")
        
        with open(image_file, 'rb') as f:
            response = requests.post(url, files={'file': f})
        
        if response.status_code == 200:
            result = response.json()
            result['filename'] = image_file.name
            results.append(result)
        else:
            print(f"  Error: {response.status_code}")
    
    return results

# Usage
results = batch_classify('./guitar_photos', model='ensemble')

# Print summary
for r in results:
    print(f"{r['filename']}: {r['predicted_class']} ({r['confidence']:.1%})")
```

---

## Rate Limiting

Currently, **no rate limiting** is applied. This may change in future versions.

---

## API Versioning

Current version: **v1**

URL structure: `http://localhost:8000/api/v1/...`

Future versions will use `/api/v2`, etc., for backward compatibility.

---

## Response Times

**Measured Performance:**

| Operation | Time (p50) | Time (p95) | Status |
|-----------|-----------|-----------|--------|
| Health Check | 8ms | 15ms | ✅ Excellent |
| Classify | 140ms | 180ms | ✅ Excellent |
| Classify-Alt | 160ms | 220ms | ✅ Excellent |
| Ensemble | 300ms | 360ms | ✅ Good |

---

## Support & Issues

For API issues:
1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Verify backend is running: `docker-compose ps`
3. Check logs: `docker-compose logs backend`
4. Visit API docs: http://localhost:8000/docs

---

*API Documentation - Guitar Classification Platform v1.0.0*  
*Last Updated: March 16, 2026*
