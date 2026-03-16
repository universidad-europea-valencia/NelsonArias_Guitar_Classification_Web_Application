# AGENTS.md - Guitar Classification Deep Learning Project - Nelson Mauricio Arias

## Project Overview
This is a Deep Learning project for classifying guitar types using TensorFlow/Keras with a pre-trained MobileNetV2 model. The main deliverable is a Jupyter Notebook that trains a CNN for image classification.

## Build, Test & Run Commands

### Running the Jupyter Notebook
```bash
# Start Jupyter locally
jupyter notebook guitar_classification_project_entregable_Nelson_Arias.ipynb

# Or run all cells in sequence
jupyter nbconvert --to notebook --execute guitar_classification_project_entregable_Nelson_Arias.ipynb --output output.ipynb
```

### Testing Single Components
```bash
# Test individual model creation
python -c "
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.models import Sequential
model = MobileNetV2(input_shape=(224, 224, 3), include_top=False, weights='imagenet')
print('MobileNetV2 loaded successfully')
"

# Verify data loading
python -c "
import os
from tensorflow.keras.preprocessing.image import ImageDataGenerator
DATA_DIR = 'guitar_images'
if os.path.exists(DATA_DIR):
    print(f'Found {len(os.listdir(DATA_DIR))} guitar classes')
"
```

### Key Dependencies
- TensorFlow >= 2.20.0
- NumPy
- Matplotlib
- Seaborn
- scikit-learn (metrics)

Install all:
```bash
pip install tensorflow>=2.20.0 numpy matplotlib seaborn scikit-learn
```

## Code Style Guidelines

### Python Code Standards
- **Imports**: Group in order: stdlib, third-party, local (blank lines between)
- **Formatting**: Follow PEP 8 style guide (4-space indentation, max 88 chars per line)
- **Naming Conventions**:
  - Constants: UPPERCASE_SNAKE_CASE (e.g., `BATCH_SIZE = 32`)
  - Variables/functions: lowercase_snake_case
  - Classes: PascalCase
  - Private methods: prefix with underscore `_private_method()`

### Type Hints
Use type hints for function parameters and returns when possible:
```python
def create_model(num_classes: int, learning_rate: float = 1e-4) -> Sequential:
    """Create a transfer learning model."""
    ...
```

### Docstrings
Use structured docstrings with numpy/scipy style:
```python
def plot_history(hist) -> None:
    """
    Plot training and validation metrics.
    
    Parameters
    ----------
    hist : keras.callbacks.History
        Training history object from model.fit()
    """
```

### Error Handling
- Use try/except blocks with specific exception types
- Always provide context in error messages
- Example:
```python
try:
    train_generator = train_datagen.flow_from_directory(DATA_DIR, ...)
except FileNotFoundError as e:
    print(f"ERROR: Dataset not found at '{DATA_DIR}'. {str(e)}")
```

### TensorFlow/Keras Conventions
- Use `tf.keras` imports (avoid `from keras`)
- Set seeds for reproducibility: `tf.random.set_seed(SEED)` and `np.random.seed(SEED)`
- Use callbacks for monitoring: EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
- Freeze base model weights in transfer learning: `base_model.trainable = False`
- Always normalize pixel values: `rescale=1./255`

### Notebook-Specific Guidelines
- Each cell should be logically self-contained with a clear purpose
- Add markdown headers before major sections
- Print informative status messages (e.g., "Found 1006 images belonging to 4 classes")
- Avoid cell interdependencies; use `if 'variable' in locals():` checks
- Keep cells focused: one model/function per cell when possible

## Configuration & Hyperparameters
Key parameters are defined at the top of the notebook:
```python
IMG_SIZE = (224, 224)      # MobileNetV2 standard input size
BATCH_SIZE = 32            # Batch size for training
SEED = 42                  # Random seed for reproducibility
DATA_DIR = 'guitar_images' # Path to training data
```

## Dataset Structure
Expected directory layout:
```
guitar_images/
├── Bajo_Electrico/        # Electric bass images
├── Guitarra_Acustica/     # Acoustic guitar images
├── Guitarra_Electrica/    # Electric guitar images
└── Guitarra_Electroacustica/  # Electroacoustic guitar images
```

## Model Architecture
Transfer Learning approach using MobileNetV2:
1. **Base Model**: Pre-trained MobileNetV2 (frozen weights)
2. **GlobalAveragePooling2D**: Converts 2D feature maps to 1D vector
3. **Dense(256, relu)**: Hidden layer with 256 units
4. **BatchNormalization**: Stabilizes training
5. **Dropout(0.5)**: Regularization (drops 50% neurons)
6. **Dense(num_classes, softmax)**: Output classification layer

## Training Strategy
- **Optimizer**: Adam (learning_rate=1e-4)
- **Loss Function**: categorical_crossentropy (multi-class classification)
- **Validation Split**: 20% of data (80% train, 20% validation)
- **Data Augmentation**: Rotation (±30°), shifts (±20%), zoom (±20%), horizontal flip
- **Callbacks**:
  - EarlyStopping: patience=6 epochs, restores best weights
  - ModelCheckpoint: saves only best model (lowest val_loss)
  - ReduceLROnPlateau: halves learning rate if no improvement for 3 epochs

## Model Evaluation
- **Metrics**: Accuracy, Loss, Precision, Recall, F1-Score
- **Confusion Matrix**: Identifies misclassified guitar types
- **Learning Curves**: Check for overfitting (gap between train/val loss)

## Expected Performance
- **Validation Accuracy**: ~85%
- **Validation Loss**: ~0.43
- **Training Time**: ~10-15 minutes (CPU, ~20 epochs with early stopping)

## File Outputs
The notebook generates:
- `best_guitar_model.keras` - Best trained model (saved during training)
- `best_guitar_model.keras` - Optional fine-tuned variant
- `best_custom_model.keras` - Optional custom CNN variant
- Training history plots (accuracy/loss curves)
- Confusion matrix visualization
- Classification report (precision/recall/F1)

## Notes for Agents
- Dataset must be in `guitar_images/` directory with class subdirectories
- Model expects 224×224 RGB images (MobileNetV2 standard)
- Seed is fixed (42) for reproducible results across runs
- Missing data directories are handled gracefully with try/except
- Model training requires GPU or will run slowly on CPU (~10+ min/epoch)
