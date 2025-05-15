#!/bin/bash

# Run all methods for evaluating and using the emotion model
# This script runs all the different scripts we've created

echo "===== Running All Emotion Model Methods ====="
echo ""

# Create output directories
mkdir -p data/evaluation
mkdir -p data/simple_model
mkdir -p data/inference_results

# 1. Check model and data format
echo "===== Checking Model and Data Format ====="
python scripts/check_model_data_format.py
echo ""

# 2. Run simple accuracy test
echo "===== Running Simple Accuracy Test ====="
python scripts/simple_accuracy_test.py
echo ""

# 3. Train simple model from scratch
echo "===== Training Simple Model from Scratch ====="
python scripts/train_simple_emotion_model.py --output_dir data/simple_model
echo ""

# 4. Run backend accuracy test
echo "===== Running Backend Accuracy Test ====="
python scripts/backend_accuracy_test.py --sample_size 100 --output data/evaluation/backend_results.json
echo ""

# 5. Run inference on sample texts
echo "===== Running Inference on Sample Texts ====="
python scripts/run_backend_inference.py --output data/inference_results
echo ""

echo "===== All Methods Complete ====="
echo ""
echo "Results can be found in:"
echo "- Simple model: data/simple_model/"
echo "- Backend evaluation: data/evaluation/"
echo "- Inference results: data/inference_results/"
echo ""
echo "For interactive inference, run:"
echo "python scripts/run_backend_inference.py --interactive"