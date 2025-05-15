#!/usr/bin/env python3
"""
Fix Emotion Model Script
-----------------------
This script fixes the emotion detection model by:
1. Downloading the dataset
2. Training the model
3. Verifying the model files
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def run_command(command, description):
    """Run a command and print its output."""
    print(f"\n{'='*80}")
    print(f"STEP: {description}")
    print(f"{'='*80}\n")
    
    print(f"Running command: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    print("\nOutput:")
    print(result.stdout)
    
    if result.returncode != 0:
        print("\nError:")
        print(result.stderr)
        return False
    
    return True

def main():
    # Create necessary directories
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("models/emotion_detector", exist_ok=True)
    
    # Step 1: Download the dataset
    print("Step 1: Downloading the dataset...")
    if not run_command("python scripts/download_dataset.py", "Download Dataset"):
        print("Failed to download the dataset. Exiting.")
        return
    
    # Verify the dataset was downloaded
    if not os.path.exists("data/raw/goemotions.csv"):
        print("Dataset file not found after download. Exiting.")
        return
    
    print("Dataset downloaded successfully!")
    
    # Step 2: Train the model
    print("\nStep 2: Training the emotion model...")
    if not run_command("python scripts/train_emotion_model.py", "Train Emotion Model"):
        print("Failed to train the model. Exiting.")
        return
    
    # Verify the model files were created
    model_pkl = Path("data/processed/emotion_model.pkl")
    model_dir = Path("models/emotion_detector")
    
    if not model_pkl.exists():
        print(f"Warning: Model file {model_pkl} was not created.")
    else:
        print(f"Model file {model_pkl} was created successfully!")
    
    if not any(model_dir.iterdir()):
        print(f"Warning: Model directory {model_dir} is empty.")
    else:
        print(f"Model files were saved to {model_dir} successfully!")
    
    # Step 3: Evaluate the model
    print("\nStep 3: Evaluating the model...")
    if not run_command("python scripts/evaluate_emotion_model.py", "Evaluate Emotion Model"):
        print("Failed to evaluate the model, but this is not critical.")
    
    print("\nFix completed! The emotion model should now work correctly.")
    print("Restart the backend service to apply the changes.")

if __name__ == "__main__":
    main()