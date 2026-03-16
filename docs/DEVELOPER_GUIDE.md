# Developer Guide

**For Contributors & Team Members**

---

## Prerequisites

- Git
- Docker 20.10+ and Docker Compose 2.0+
- Python 3.10+ (for local development)
- Node.js 18+ (for local frontend development)
- Code editor (VS Code recommended)

---

## Local Development Setup

### 1. Clone Repository

```bash
git clone <repo-url>
cd NelsonArias_Guitar_Classification_Web_Application
```

### 2. With Docker (Recommended)

```bash
# Start services
docker-compose up -d --build

# Run tests
docker-compose exec backend python -m pytest tests/ -v
docker-compose exec frontend npm test

# Stop services
docker-compose down
```

### 3. Local Python Setup (Backend)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Run server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
python -m pytest tests/ -v --cov=app
```

### 4. Local Node Setup (Frontend)

```bash
# Install dependencies
cd frontend
npm install

# Start development server
npm start

# Run tests
npm test

# Build for production
npm run build
```

---

## Code Style & Standards

### Python (PEP 8)

```python
# Good
def classify_image(file_path: str) -> dict:
    """Classify guitar image and return predictions."""
    ...

# Bad
def classifyImage(filePath):
    ...
```

### JavaScript/React (ESLint)

```javascript
// Good
const classifyImage = async (file) => {
  const response = await api.classify(file);
  return response;
};

// Bad
const classifyImage = function(file){
  return api.classify(file);
}
```

### Formatting

```bash
# Python formatting (backend)
pip install black
black backend/

# JavaScript formatting (frontend)
npm install --save-dev prettier
npx prettier --write frontend/src
```

---

## Git Workflow

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "feat: Add new feature description"

# Push to remote
git push origin feature/new-feature

# Create pull request on GitHub
```

### Commit Message Convention

```
<type>: <description>

<optional body>
<optional footer>
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`

---

## Testing

### Backend Tests

```bash
# All tests
python -m pytest tests/ -v

# Specific test file
python -m pytest tests/test_integration.py -v

# With coverage
python -m pytest tests/ --cov=app --cov-report=html

# Specific test class
python -m pytest tests/test_image_service.py::TestImageProcessor -v
```

### Frontend Tests

```bash
# Run all tests
npm test

# Watch mode
npm test -- --watch

# Coverage report
npm test -- --coverage
```

### Writing Tests

**Backend (pytest):**
```python
def test_classify_valid_image():
    """Test classification with valid image."""
    # Arrange
    processor = ImageProcessor()
    
    # Act
    result = processor.preprocess(test_image)
    
    # Assert
    assert result is not None
    assert result.shape == (1, 224, 224, 3)
```

**Frontend (Jest):**
```javascript
test('ImageUploader renders upload button', () => {
  const { getByText } = render(<ImageUploader />);
  expect(getByText('Upload')).toBeInTheDocument();
});
```

---

## Adding Features

### Backend Endpoint

```python
# 1. Create route in app/routes/new_feature.py
from fastapi import APIRouter
router = APIRouter()

@router.post("/new-endpoint")
async def new_endpoint(request: Request):
    """New endpoint description."""
    return {"result": "value"}

# 2. Add to main.py
app.include_router(new_feature.router, prefix="/api/v1")

# 3. Write tests in tests/test_new_feature.py
def test_new_endpoint():
    response = client.post("/api/v1/new-endpoint")
    assert response.status_code == 200

# 4. Update API.md documentation
```

### Frontend Component

```javascript
// 1. Create component
// src/components/NewComponent.js
export const NewComponent = ({ prop1 }) => {
  return <div>{prop1}</div>;
};

// 2. Use in App.js
import { NewComponent } from './components/NewComponent';

// 3. Write tests
test('NewComponent renders prop', () => {
  render(<NewComponent prop1="value" />);
  expect(screen.getByText('value')).toBeInTheDocument();
});

// 4. Update README
```

---

## Debugging

### Backend Debugging

```bash
# With print statements
print(f"Debug: {variable}")

# With logging
import logging
logger = logging.getLogger(__name__)
logger.info(f"Processing image: {filename}")

# With debugger
import pdb; pdb.set_trace()
```

### Frontend Debugging

```javascript
// Console logging
console.log('Debug:', variable);

// React DevTools browser extension
// Breakpoints in VS Code

// React Profiler
// Performance monitoring
```

### Docker Debugging

```bash
# View container logs
docker-compose logs backend -f

# Execute command in container
docker-compose exec backend bash

# View running processes
docker-compose ps

# Inspect container
docker inspect <container-name>
```

---

## Performance Optimization

### Backend

- Profile inference time
- Monitor memory usage
- Batch process images
- Cache model results
- Optimize image preprocessing

### Frontend

- Lazy load components
- Memoize expensive computations
- Optimize bundle size
- Use React DevTools Profiler
- Enable compression

---

## Database Integration (Future)

```python
# When adding database support:
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 1. Create models in app/models/
# 2. Setup migrations with Alembic
# 3. Add database routes
# 4. Write database tests
```

---

## Deployment Checklist

- [ ] All tests passing (backend + frontend)
- [ ] Code reviewed
- [ ] Documentation updated
- [ ] Docker images build successfully
- [ ] Environment variables configured
- [ ] Health checks passing
- [ ] Performance benchmarks met
- [ ] Security audit completed

---

## Common Issues

### Issue: Port Already in Use

```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Issue: Docker Build Fails

```bash
# Clean build
docker-compose down -v
docker-compose up -d --build

# Check Docker logs
docker-compose logs backend
```

### Issue: Tests Failing

```bash
# Clear cache
find . -type d -name __pycache__ -exec rm -r {} +

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

---

## Useful Commands

```bash
# Docker
docker-compose up -d           # Start services
docker-compose down            # Stop services
docker-compose logs -f         # View logs
docker-compose exec backend bash   # Execute in container

# Python
python -m pytest tests/         # Run tests
python -m black .              # Format code
python -m mypy app/            # Type checking

# Node
npm install                    # Install dependencies
npm test                       # Run tests
npm run build                  # Build production

# Git
git status                     # Check status
git diff                       # View changes
git log --oneline              # View commits
```

---

## Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)
- [Docker Docs](https://docs.docker.com/)
- [pytest Docs](https://docs.pytest.org/)
- [GitHub Guides](https://guides.github.com/)

---

*Developer Guide - Guitar Classification Platform*  
*Last Updated: March 16, 2026*
