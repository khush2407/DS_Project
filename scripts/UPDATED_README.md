# Emotion Model Scripts

This directory contains scripts for training, evaluating, and using the emotion detection model.

## Available Scripts

### Original Scripts
- `train_emotion_model.py`: Trains the emotion detection model on the GoEmotions dataset
- `analyze_dataset.py`: Analyzes the GoEmotions dataset and generates statistics
- `create_simple_model.py`: Creates a simple placeholder model for testing
- `create_placeholder_model.py`: Creates a placeholder model for testing
- `download_dataset.py`: Downloads the GoEmotions dataset
- `preprocess_data.py`: Preprocesses the GoEmotions dataset for training

### New Scripts for Model Evaluation
- `check_model_data_format.py`: Checks the format of model and data files
- `simple_accuracy_test.py`: Runs a simple accuracy test using TF-IDF + Logistic Regression
- `backend_accuracy_test.py`: Uses the backend emotion service to evaluate accuracy
- `train_simple_emotion_model.py`: Trains a simple TF-IDF + Logistic Regression model from scratch
- `run_backend_inference.py`: Uses the backend emotion service for inference on custom text
- `run_all_methods.sh`: Shell script to run all evaluation methods in sequence

## Understanding the Data and Model Format

After investigation, we discovered that:

1. The model file (`data/processed/emotion_model.pkl`) is a simple dictionary with keys like "layer_0.weight", "layer_0.bias", etc. This is from the `create_simple_model.py` script that creates a placeholder model, not a real trained model.

2. The data files (`data/processed/test.pkl`, `data/processed/train.pkl`, `data/processed/val.pkl`) are pandas DataFrames, not tuples of (texts, labels) as expected by our original evaluation scripts.

To check the format of your model and data files, run:

```bash
python scripts/check_model_data_format.py
```

## Getting Model Accuracy

Given the actual format of the data and model files, here are the recommended ways to get accuracy:

### 1. Using the Simple Accuracy Test

The `simple_accuracy_test.py` script trains a simple TF-IDF + Logistic Regression model on the training data and evaluates it on the test data:

```bash
python scripts/simple_accuracy_test.py
```

Options:
- `--train_data`: Path to the training data (default: data/processed/train.pkl)
- `--test_data`: Path to the test data (default: data/processed/test.pkl)
- `--sample_size`: Number of examples to sample for training (default: use all)

### 2. Using the Backend Emotion Service

The `backend_accuracy_test.py` script uses the existing emotion service from the backend to evaluate accuracy:

```bash
python scripts/backend_accuracy_test.py
```

Options:
- `--test_data`: Path to the test data (default: data/processed/test.pkl)
- `--sample_size`: Number of examples to sample for evaluation (default: 100)
- `--output`: Path to save the evaluation results (default: data/evaluation/backend_results.json)

### 3. Training a Simple Model from Scratch

The `train_simple_emotion_model.py` script trains a simple TF-IDF + Logistic Regression model from scratch and evaluates it:

```bash
python scripts/train_simple_emotion_model.py
```

Options:
- `--data`: Path to the training data (default: data/processed/train.pkl)
- `--test_size`: Proportion of data to use for testing (default: 0.2)
- `--output_dir`: Directory to save the model and results (default: data/simple_model)

This script will:
- Train a TF-IDF + Logistic Regression model on the training data
- Evaluate the model on the test data
- Save the model, metrics, and visualizations to the output directory

## Running Inference

### Using the Backend Inference Script

The easiest way to run inference is to use the `run_backend_inference.py` script:

```bash
python scripts/run_backend_inference.py --text "I am feeling happy today"
```

Options:
- `--text`: Text to analyze
- `--file`: File containing text to analyze (one text per line)
- `--output`: Output directory for results and plots
- `--interactive`: Run in interactive mode

Interactive mode allows you to enter multiple texts for analysis:

```bash
python scripts/run_backend_inference.py --interactive
```

You can also run the script without arguments to analyze sample texts:

```bash
python scripts/run_backend_inference.py --output data/inference_results
```

### Using the Backend Emotion Service Directly

You can also use the backend emotion service directly in your Python code:

```python
from backend.services.emotion_service import EmotionService

# Initialize the emotion service
emotion_service = EmotionService()

# Run inference
emotions, primary_emotion = emotion_service.detect_emotions("I am feeling happy today")

print(f"Primary emotion: {primary_emotion}")
print("Top emotions:")
for emotion, prob in sorted(emotions.items(), key=lambda x: x[1], reverse=True)[:5]:
    print(f"  {emotion}: {prob:.4f}")

# Get emotion summary
summary = emotion_service.get_emotion_summary(emotions)
print(f"\nEmotion summary:\n{summary}")
```

## Example Workflows

### Running All Methods at Once

The easiest way to run all the evaluation methods is to use the provided shell script:

```bash
bash scripts/run_all_methods.sh
```

This script will:
1. Check the format of your model and data files
2. Run a simple accuracy test
3. Train a simple model from scratch
4. Use the backend emotion service for evaluation
5. Run inference on sample texts

All results will be saved to appropriate directories for review.

### Manual Workflow

If you prefer to run the scripts individually:

1. Check the format of your model and data files:
   ```bash
   python scripts/check_model_data_format.py
   ```

2. Run a simple accuracy test:
   ```bash
   python scripts/simple_accuracy_test.py
   ```

3. Train a simple model from scratch:
   ```bash
   python scripts/train_simple_emotion_model.py
   ```

4. Use the backend emotion service for evaluation:
   ```bash
   python scripts/backend_accuracy_test.py
   ```

5. Run inference on custom text:
   ```bash
   python scripts/run_backend_inference.py --interactive
   ```

## Notes on the Current Model

The current model in `data/processed/emotion_model.pkl` is a placeholder model created by `create_simple_model.py`. It's not a trained model and won't give meaningful predictions. To get accurate results, you should either:

1. Train a real model using `train_emotion_model.py` (which may require fixing the script to handle the actual data format)
2. Use the simple model trained by `train_simple_emotion_model.py`
3. Use the backend emotion service, which falls back to a keyword-based approach if the model can't be loaded

## Troubleshooting

If you encounter errors with the scripts, check the following:

1. Make sure you're running the scripts from the project root directory
2. Check the format of your model and data files using `check_model_data_format.py`
3. If the model file is not in the expected format, try using the backend emotion service or training a simple model from scratch