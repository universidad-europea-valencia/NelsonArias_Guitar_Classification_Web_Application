# System Architecture

**Guitar Classification Platform - Technical Architecture**

---

## System Overview

```
┌──────────────────────────────────────────────────────────────┐
│                   User's Web Browser                         │
│                   (React Frontend)                           │
└────────────────────┬─────────────────────────────────────────┘
                     │ HTTP/REST (Port 3000)
                     │
┌────────────────────▼─────────────────────────────────────────┐
│              Frontend Application (React)                     │
│  ├─ Components (Header, ImageUploader, Results)             │
│  ├─ API Service Layer (HTTP client)                         │
│  ├─ State Management (React Hooks)                          │
│  └─ CSS Styling (Responsive Design)                         │
└────────────────────┬─────────────────────────────────────────┘
                     │ HTTP/REST (Port 8000)
                     │
┌────────────────────▼─────────────────────────────────────────┐
│           Backend API Server (FastAPI)                        │
│  ├─ Routes: /api/v1/{classify, health}                       │
│  ├─ Request Validation (Pydantic)                            │
│  ├─ Error Handling & Logging                                 │
│  └─ CORS & Security Middleware                               │
└────────────────────┬─────────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────────┐
│       ML Services Layer (Python Services)                     │
│  ├─ ModelManager (LRU Cache, Lazy Loading)                   │
│  ├─ ImageProcessor (Validation, Resize, Normalize)           │
│  └─ PredictionService (Inference, Ensemble)                  │
└────────────────────┬─────────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────────┐
│    TensorFlow/Keras Inference Engine                          │
│  ├─ Model 1: best_guitar_model.keras (MobileNetV2)          │
│  └─ Model 2: best_transfer_model.keras (Alternative)         │
│                                                              │
│  4 Output Classes:                                           │
│  ├─ Bajo_Electrico                                           │
│  ├─ Guitarra_Acustica                                        │
│  ├─ Guitarra_Electrica                                       │
│  └─ Guitarra_Electroacustica                                 │
└──────────────────────────────────────────────────────────────┘
```

---

## Component Architecture

### Frontend (React)

**Directory Structure:**
```
frontend/src/
├── components/
│   ├── Header.js          # Top navigation bar
│   ├── ImageUploader.js   # File upload with D&D
│   ├── Results.js         # Results display
│   └── ...
├── services/
│   └── api.js            # HTTP client (Axios)
├── App.js                # Main application
└── index.js              # Entry point
```

**Key Features:**
- Responsive React 18 with hooks
- Drag-and-drop image upload
- Real-time API status monitoring
- Confidence visualization (gauges, charts)
- Model selection dropdown
- Error display with retry capability

### Backend (FastAPI)

**Directory Structure:**
```
backend/app/
├── core/
│   └── config.py         # Configuration & settings
├── routes/
│   ├── classification.py # POST /classify endpoints
│   └── health.py         # GET /health endpoint
├── services/
│   ├── model_service.py  # ModelManager with LRU cache
│   ├── image_service.py  # ImageProcessor
│   └── prediction_service.py  # Inference engine
├── schemas/
│   └── __init__.py       # Pydantic models
└── main.py              # FastAPI app setup
```

**Design Patterns:**
- Lazy Loading: Models loaded on first use
- LRU Cache: Memory management (maxsize=2)
- Dependency Injection: Service composition
- Error Handling: Graceful degradation

### ML Services Layer

**ModelManager (model_service.py)**
```python
- @lru_cache(maxsize=2): Limits memory usage
- get_model(): Load models on demand
- clear_cache(): Free memory when needed
```

**ImageProcessor (image_service.py)**
```python
- preprocess(): Validation, resize, normalize
- validate_file(): Check format, size, corruption
- _process_image(): Actual processing logic
```

**PredictionService (prediction_service.py)**
```python
- predict_primary(): Single model inference
- predict_ensemble(): Average probabilities
- process_probabilities(): Format results
```

---

## Data Flow

### Classification Request Flow

```
1. User Upload
   └─> Browser: Image file selected/dropped
   
2. Frontend Processing
   └─> React: Validate file locally
   └─> API: POST /classify with FormData
   
3. Backend Routing
   └─> FastAPI: Route to /classify endpoint
   └─> Validation: Check file size, type
   
4. ML Pipeline
   └─> ImageProcessor: Load → Validate → Resize → Normalize
   └─> ModelManager: Lazy load model (or retrieve from cache)
   └─> PredictionService: Run inference
   
5. Response Generation
   └─> Format: Calculate confidence, top-3 predictions
   └─> Timing: Measure processing time
   └─> Return: JSON response
   
6. Frontend Display
   └─> React: Update state with results
   └─> UI: Show confidence gauge, predictions, timing
```

---

## Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Frontend** | React | 18.2+ | UI framework |
| | Axios | 1.6+ | HTTP client |
| | CSS3 | - | Styling |
| **Backend** | FastAPI | 0.104+ | Web framework |
| | Uvicorn | 0.24+ | ASGI server |
| | Pydantic | 2.5+ | Data validation |
| **ML** | TensorFlow | 2.14+ | Deep learning |
| | Keras | 2.14+ | Model API |
| | NumPy | 1.24+ | Numerical computing |
| | Pillow | 10.1+ | Image processing |
| **Testing** | pytest | 7.0+ | Backend tests |
| | Jest | 27.0+ | Frontend tests |
| | unittest | - | Python std |
| **DevOps** | Docker | 20.10+ | Containerization |
| | Docker Compose | 2.0+ | Orchestration |

---

## API Design

### REST Conventions

**Endpoints:**
- `GET /api/v1/health` - Health check
- `POST /api/v1/classify` - Primary model
- `POST /api/v1/classify-alternative` - Alternative model
- `POST /api/v1/classify-ensemble` - Both models

**Status Codes:**
- 200 OK - Successful classification
- 400 Bad Request - Invalid file
- 422 Unprocessable Entity - Validation error
- 500 Internal Server Error - Processing failure

**Response Format:**
```json
{
  "predicted_class": "String",
  "confidence": 0.0-1.0,
  "processing_time_ms": Number,
  "all_probabilities": { "class": confidence },
  "model_used": "String"
}
```

---

## Performance Considerations

### Model Loading
- **Method:** Lazy loading on first use
- **Caching:** LRU cache (maxsize=2)
- **Memory:** ~20MB per model
- **Load Time:** <500ms

### Image Processing
- **Resize:** Pillow LANCZOS (quality)
- **Normalization:** 0-1 range
- **Batch Support:** Multiple images
- **Validation:** File type, size, corruption check

### Inference
- **Batch Size:** Variable (default 1)
- **Device:** CPU (GPU if available)
- **Response Time:** ~150-200ms per image
- **Throughput:** ~5-6 images/sec (CPU)

---

## Scalability Architecture

### Current Limits
- Models in Memory: 2 (LRU cache)
- Concurrent Requests: ~50 (thread pool)
- Batch Size: Variable (memory dependent)

### Future Enhancements
- Redis caching for model persistence
- Kubernetes orchestration
- GPU acceleration support
- Load balancing with multiple instances
- Database for result history

---

## Security Architecture

### Input Validation
- File type verification (magic bytes)
- File size limits (4MB)
- Image corruption detection
- Filename sanitization

### Request Security
- CORS middleware (configured)
- TrustedHost middleware (configured)
- Error message sanitization
- No sensitive info in logs

### Model Protection
- Models in secure location
- No model export/download
- Inference-only exposure

---

## Monitoring & Logging

### Health Checks
- API endpoint: `/api/v1/health`
- Frequency: Every 30 seconds (frontend)
- Response: Status, timestamp, version

### Logging
- **Backend:** INFO level, structured format
- **Frontend:** Console logs, error reporting
- **Metrics:** Response times, request counts

### Error Tracking
- Try-catch at service boundaries
- Graceful error responses
- Detailed backend logs
- User-friendly frontend messages

---

## Deployment Architecture

### Docker Containers

**Backend Container:**
- Base Image: `python:3.10-slim`
- Port: 8000
- Health Check: HTTP GET /api/v1/health

**Frontend Container:**
- Build Stage: Node 18-alpine
- Runtime Stage: Nginx serving
- Port: 3000

### Orchestration (docker-compose)
```yaml
- Backend service (FastAPI)
- Frontend service (React/Nginx)
- Network: Bridge (services communicate)
- Volumes: Models, code (dev mode)
```

---

## Extension Points

### Adding New Models
1. Place model file in `models/` directory
2. Update ModelManager to load new model
3. Add new prediction endpoint
4. Update tests and documentation

### Adding New Endpoints
1. Create route in `routes/`
2. Implement service layer logic
3. Add validation with Pydantic
4. Write tests
5. Update API documentation

### Adding New Features
1. Define requirements
2. Implement in isolated service
3. Add comprehensive tests
4. Update documentation
5. Deploy via Docker

---

*System Architecture - Guitar Classification Platform v1.0.0*  
*Last Updated: March 16, 2026*
