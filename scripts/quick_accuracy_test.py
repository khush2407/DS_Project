import torch
import pickle
import os
import numpy as np
import random
import argparse
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

# Define emotion labels
emotion_labels = [
    "neutral", "approval", "admiration", "annoyance", "gratitude",
    "disapproval", "curiosity", "amusement", "realization", "optimism",
    "disappointment", "love", "anger", "joy", "confusion", "sadness",
    "caring", "excitement", "surprise", "disgust", "desire", "fear",
    "remorse", "embarrassment", "nervousness", "pride", "relief", "grief"
]

def load_model(model_path, full_model_path):
    """Load the pre-trained model."""
    print("Loading model...")
    
    # Initialize model and tokenizer
    tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
    
    # Try loading from full model path first
    if os.path.exists(full_model_path):
        try:
            print(f"Loading full model from {full_model_path}")
            model = AutoModelForSequenceClassification.from_pretrained(full_model_path)
            print("Successfully loaded full model")
            return model, tokenizer
        except Exception as e:
            print(f"Error loading full model: {e}")
            print("Falling back to state dict loading")
    
    # Load from state dict
    model = AutoModelForSequenceClassification.from_pretrained(
        "distilbert-base-uncased",
        num_labels=len(emotion_labels),
        problem_type="multi_label_classification"
    )
    
    # Try to load from saved model path
    if os.path.exists(model_path):
        try:
            print(f"Loading fine-tuned model from {model_path}")
            with open(model_path, 'rb') as f:
                model_state = pickle.load(f)
                if isinstance(model_state, dict):
                    model.load_state_dict(model_state)
                    print("Successfully loaded fine-tuned model weights")
                else:
                    print("Warning: Model file does not contain valid state dictionary")
        except Exception as e:
            print(f"Error loading fine-tuned model: {e}")
            print("Using base model instead")
    else:
        print("No fine-tuned model found. Using base model.")
    
    return model, tokenizer

def load_test_data(data_path, sample_size=100):
    """Load a sample of test data."""
    print(f"Loading test data from {data_path}")
    
    try:
        with open(data_path, 'rb') as f:
            data = pickle.load(f)
            
        if isinstance(data, tuple) and len(data) == 2:
            texts, labels = data
            
            # Sample data
            if sample_size and sample_size < len(texts):
                indices = random.sample(range(len(texts)), sample_size)
                texts = [texts[i] for i in indices]
                labels = labels[indices] if labels is not None else None
            
            return texts, labels
        else:
            print("Unexpected format in data file")
            return None, None
    except Exception as e:
        print(f"Error loading data: {e}")
        return None, None

def run_quick_test(model, tokenizer, texts, labels, device):
    """Run a quick accuracy test on a sample of data."""
    print("Running quick accuracy test...")
    
    model.to(device)
    model.eval()
    
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for i, (text, label) in enumerate(zip(texts, labels)):
            # Tokenize
            inputs = tokenizer(
                text,
                padding=True,
                truncation=True,
                max_length=128,
                return_tensors="pt"
            )
            
            # Move to device
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            # Get predictions
            outputs = model(**inputs)
            logits = outputs.logits
            
            # Convert to probabilities and binary predictions
            probs = torch.sigmoid(logits).cpu().numpy()
            preds = (probs > 0.5).astype(int)
            
            all_preds.append(preds[0])
            all_labels.append(label)
            
            # Print progress
            if (i + 1) % 10 == 0:
                print(f"Processed {i + 1}/{len(texts)} examples")
    
    # Calculate metrics
    all_preds = np.array(all_preds)
    all_labels = np.array(all_labels)
    
    accuracy = accuracy_score(all_labels, all_preds)
    f1 = f1_score(all_labels, all_preds, average='weighted', zero_division=0)
    precision = precision_score(all_labels, all_preds, average='weighted', zero_division=0)
    recall = recall_score(all_labels, all_preds, average='weighted', zero_division=0)
    
    return {
        "accuracy": accuracy,
        "f1": f1,
        "precision": precision,
        "recall": recall
    }

def main():
    parser = argparse.ArgumentParser(description="Run a quick accuracy test on the emotion model")
    parser.add_argument("--model_path", type=str, default="data/processed/emotion_model.pkl",
                        help="Path to the model state dict")
    parser.add_argument("--full_model_path", type=str, default="models/emotion_detector",
                        help="Path to the full model directory")
    parser.add_argument("--test_data", type=str, default="data/processed/test.pkl",
                        help="Path to the test data")
    parser.add_argument("--sample_size", type=int, default=100,
                        help="Number of examples to sample for the quick test")
    args = parser.parse_args()
    
    # Set device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Load model
    model, tokenizer = load_model(args.model_path, args.full_model_path)
    
    # Load test data
    texts, labels = load_test_data(args.test_data, args.sample_size)
    
    if texts is None or labels is None:
        print("Failed to load test data. Exiting.")
        return
    
    # Run quick test
    metrics = run_quick_test(model, tokenizer, texts, labels, device)
    
    # Print results
    print("\nQuick Accuracy Test Results:")
    print(f"Sample Size: {len(texts)}")
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print(f"F1 Score: {metrics['f1']:.4f}")
    print(f"Precision: {metrics['precision']:.4f}")
    print(f"Recall: {metrics['recall']:.4f}")

if __name__ == "__main__":
    main()