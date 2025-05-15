#!/bin/bash

# Run all evaluation methods for the emotion model
# This script runs all the different ways to evaluate the model's accuracy

echo "===== Running All Emotion Model Evaluations ====="
echo ""

# Create output directories
mkdir -p data/evaluation
mkdir -p data/visualization

# 1. Quick Accuracy Test
echo "===== Running Quick Accuracy Test ====="
python scripts/quick_accuracy_test.py --sample_size 100
echo ""

# 2. Full Evaluation
echo "===== Running Full Model Evaluation ====="
python scripts/evaluate_emotion_model.py --test_data data/processed/test.pkl
echo ""

# 3. Visualize Results
echo "===== Visualizing Evaluation Results ====="
python scripts/visualize_model_results.py
echo ""

# 4. Run Inference on Sample Texts
echo "===== Running Inference on Sample Texts ====="
mkdir -p data/inference_samples

# Sample texts representing different emotions
python scripts/run_emotion_inference.py --text "I am feeling really happy today!" --output data/inference_samples
python scripts/run_emotion_inference.py --text "I'm so angry about what happened yesterday." --output data/inference_samples
python scripts/run_emotion_inference.py --text "I'm feeling anxious about my upcoming presentation." --output data/inference_samples
python scripts/run_emotion_inference.py --text "I'm so sad about the news." --output data/inference_samples
python scripts/run_emotion_inference.py --text "I'm surprised by the unexpected turn of events." --output data/inference_samples

echo ""
echo "===== All Evaluations Complete ====="
echo ""
echo "Results can be found in:"
echo "- Quick test results: Displayed in terminal"
echo "- Full evaluation: data/evaluation/"
echo "- Visualizations: data/visualization/"
echo "- Inference samples: data/inference_samples/"