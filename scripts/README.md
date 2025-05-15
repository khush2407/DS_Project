# Emotion Model Scripts

This directory contains scripts for training, evaluating, and using the emotion detection model.

## Available Scripts

- `train_emotion_model.py`: Trains the emotion detection model on the GoEmotions dataset
- `evaluate_emotion_model.py`: Evaluates the trained model on a test dataset
- `run_emotion_inference.py`: Runs inference with the trained model on custom text inputs
- `quick_accuracy_test.py`: Runs a quick accuracy test on a sample of test data
- `visualize_model_results.py`: Visualizes the evaluation results from training or evaluation
- `emotion_model_web_ui.py`: Provides a web interface for interacting with the model
- `run_all_evaluations.sh`: Shell script to run all evaluation methods in sequence
- `analyze_dataset.py`: Analyzes the GoEmotions dataset and generates statistics
- `create_simple_model.py`: Creates a simple placeholder model for testing
- `create_placeholder_model.py`: Creates a placeholder model for testing
- `download_dataset.py`: Downloads the GoEmotions dataset
- `preprocess_data.py`: Preprocesses the GoEmotions dataset for training

## Getting Model Accuracy

There are several ways to get the accuracy of the emotion detection model:

### 1. Using the Evaluation Script

The `evaluate_emotion_model.py` script evaluates the trained model on a test dataset and calculates accuracy metrics:

```bash
python scripts/evaluate_emotion_model.py --test_data data/processed/test.pkl
```

Options:
- `--model_path`: Path to the model file (default: data/processed/emotion_model.pkl)
- `--test_data`: Path to the test data file (default: data/processed/test.pkl)
- `--batch_size`: Batch size for evaluation (default: 32)

The script will output:
- Accuracy, F1 score, precision, and recall metrics
- Per-class metrics for each emotion
- Confusion matrix visualization
- All results are saved to `data/evaluation/`

### 2. Quick Accuracy Test

For a fast estimate of model accuracy on a small sample of test data:

```bash
python scripts/quick_accuracy_test.py
```

Options:
- `--model_path`: Path to the model state dict (default: data/processed/emotion_model.pkl)
- `--full_model_path`: Path to the full model directory (default: models/emotion_detector)
- `--test_data`: Path to the test data (default: data/processed/test.pkl)
- `--sample_size`: Number of examples to sample for the quick test (default: 100)

This script runs much faster than the full evaluation and gives you a quick estimate of model performance.

### 3. Visualizing Existing Evaluation Results

If you've already trained the model, evaluation results are saved to `data/processed/eval_results.json`. You can visualize these results using:

```bash
python scripts/visualize_model_results.py
```

Options:
- `--results`: Path to evaluation results JSON file (default: data/processed/eval_results.json)
- `--output`: Output directory for visualizations (default: data/visualization)

This will generate visualizations of:
- Overall metrics (accuracy, F1, precision, recall)
- Per-class metrics for top and bottom emotions
- Confusion matrix (if available)

### 4. Retraining the Model

You can retrain the model and get accuracy metrics during training:

```bash
python scripts/train_emotion_model.py
```

The training script automatically evaluates the model on a validation set and prints accuracy metrics after each epoch. The final evaluation results are saved to `data/processed/eval_results.json`.

## Running Inference

### Command Line Interface

To run inference with the trained model on custom text:

```bash
python scripts/run_emotion_inference.py --text "I am feeling happy today"
```

Options:
- `--text`: Text to analyze
- `--file`: File containing text to analyze
- `--model_path`: Path to model state dict (default: data/processed/emotion_model.pkl)
- `--full_model_path`: Path to full model directory (default: models/emotion_detector)
- `--output`: Output directory for plots
- `--interactive`: Run in interactive mode

Interactive mode allows you to enter multiple texts for analysis:

```bash
python scripts/run_emotion_inference.py --interactive
```

### Web Interface

For a more user-friendly experience, you can use the Streamlit web interface:

```bash
streamlit run scripts/emotion_model_web_ui.py
```

This will launch a web application where you can:
- Enter text to analyze
- Try sample texts with different emotions
- View the primary emotion and emotion distribution
- See a visualization of the emotion probabilities

Requirements:
- Streamlit: `pip install streamlit`

## Example Workflows

### Manual Workflow

1. Train the model (if not already trained):
   ```bash
   python scripts/train_emotion_model.py
   ```

2. Run a quick accuracy test:
   ```bash
   python scripts/quick_accuracy_test.py
   ```

3. Evaluate the model on the full test set:
   ```bash
   python scripts/evaluate_emotion_model.py
   ```

4. Visualize the evaluation results:
   ```bash
   python scripts/visualize_model_results.py
   ```

5. Run inference on custom text:
   ```bash
   python scripts/run_emotion_inference.py --interactive
   ```

### Automated Evaluation

To run all evaluation methods in sequence, use the provided shell script:

```bash
bash scripts/run_all_evaluations.sh
```

This script will:
1. Run a quick accuracy test on a sample of 100 examples
2. Run a full evaluation on the test set
3. Generate visualizations of the evaluation results
4. Run inference on sample texts representing different emotions

All results will be saved to appropriate directories for review.

## Additional Resources

- The trained model is saved in two formats:
  - State dictionary: `data/processed/emotion_model.pkl`
  - Full model and tokenizer: `models/emotion_detector/`

- Evaluation results are saved to:
  - `data/processed/eval_results.json` (from training)
  - `data/evaluation/` (from evaluation script)
  - `data/visualization/` (from visualization script)

- For a user-friendly interface, use the web UI:
  ```bash
  streamlit run scripts/emotion_model_web_ui.py
  ```

## Model Files

The trained model is saved in two formats:
- State dictionary: `data/processed/emotion_model.pkl`
- Full model and tokenizer: `models/emotion_detector/`

Both formats can be used for inference and evaluation.