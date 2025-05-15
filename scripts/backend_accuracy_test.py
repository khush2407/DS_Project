import sys
import os
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
import argparse
from tqdm import tqdm
import json

# Add the backend directory to the path so we can import the services
sys.path.append(os.path.abspath('backend'))

# Import the emotion service
try:
    from services.emotion_service import EmotionService
    print("Successfully imported EmotionService from backend")
except ImportError as e:
    print(f"Error importing EmotionService: {e}")
    print("Make sure you're running this script from the project root directory")
    sys.exit(1)

def load_data(data_path):
    """Load data from pickle file."""
    print(f"Loading data from {data_path}")
    
    try:
        # Load the DataFrame
        df = pd.read_pickle(data_path)
        print(f"Successfully loaded DataFrame with shape {df.shape}")
        
        # Identify text column
        text_col = None
        for col in df.columns:
            if col.lower() in ['text', 'content', 'message', 'comment']:
                text_col = col
                break
        
        if text_col is None:
            # Assume first column is text
            text_col = df.columns[0]
        
        print(f"Using '{text_col}' as text column")
        
        # Extract texts
        texts = df[text_col].tolist()
        
        # Extract labels (all columns except text column)
        label_cols = [col for col in df.columns if col != text_col]
        
        # Check if we have numeric columns for labels
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if numeric_cols:
            label_cols = [col for col in numeric_cols if col != text_col]
        
        if not label_cols:
            print("No label columns found. Cannot proceed with evaluation.")
            return None, None, None
        
        print(f"Using {len(label_cols)} columns as labels: {label_cols[:5]}...")
        labels = df[label_cols].values
        
        return texts, labels, label_cols
    
    except Exception as e:
        print(f"Error loading data: {e}")
        return None, None, None

def evaluate_with_emotion_service(emotion_service, texts, labels, label_cols, emotion_labels, sample_size=None):
    """Evaluate the emotion service on the given texts and labels."""
    print("Evaluating with EmotionService...")
    
    # Sample data if requested
    if sample_size and sample_size < len(texts):
        indices = np.random.choice(len(texts), sample_size, replace=False)
        texts = [texts[i] for i in indices]
        labels = labels[indices]
        print(f"Sampled {sample_size} examples for evaluation")
    
    # Create a mapping from emotion labels to indices
    emotion_to_idx = {emotion: i for i, emotion in enumerate(emotion_labels)}
    
    # Create a mapping from label columns to emotion labels
    label_col_to_emotion = {}
    for col in label_cols:
        col_lower = col.lower()
        for emotion in emotion_labels:
            if emotion.lower() in col_lower or col_lower in emotion.lower():
                label_col_to_emotion[col] = emotion
                break
    
    print(f"Mapped {len(label_col_to_emotion)} label columns to emotions")
    
    # Process texts and get predictions
    all_preds = []
    all_labels = []
    
    for i, text in enumerate(tqdm(texts, desc="Processing texts")):
        try:
            # Get predictions from emotion service
            emotions, primary_emotion = emotion_service.detect_emotions(text)
            
            # Convert predictions to binary format
            pred = np.zeros(len(label_cols))
            for col_idx, col in enumerate(label_cols):
                if col in label_col_to_emotion:
                    emotion = label_col_to_emotion[col]
                    if emotion in emotions:
                        pred[col_idx] = 1 if emotions[emotion] > 0.5 else 0
            
            all_preds.append(pred)
            all_labels.append(labels[i])
            
            # Print progress
            if (i + 1) % 50 == 0:
                print(f"Processed {i + 1}/{len(texts)} examples")
        
        except Exception as e:
            print(f"Error processing text {i}: {e}")
            # Use a zero vector as fallback
            all_preds.append(np.zeros(len(label_cols)))
            all_labels.append(labels[i])
    
    # Convert to numpy arrays
    all_preds = np.array(all_preds)
    all_labels = np.array(all_labels)
    
    # Calculate metrics
    accuracy = accuracy_score(all_labels, all_preds)
    f1 = f1_score(all_labels, all_preds, average='weighted', zero_division=0)
    precision = precision_score(all_labels, all_preds, average='weighted', zero_division=0)
    recall = recall_score(all_labels, all_preds, average='weighted', zero_division=0)
    
    return {
        "accuracy": float(accuracy),
        "f1": float(f1),
        "precision": float(precision),
        "recall": float(recall)
    }

def main():
    parser = argparse.ArgumentParser(description="Evaluate the backend emotion service on test data")
    parser.add_argument("--test_data", type=str, default="data/processed/test.pkl",
                        help="Path to the test data")
    parser.add_argument("--sample_size", type=int, default=100,
                        help="Number of examples to sample for evaluation")
    parser.add_argument("--output", type=str, default="data/evaluation/backend_results.json",
                        help="Path to save the evaluation results")
    args = parser.parse_args()
    
    # Initialize the emotion service
    emotion_service = EmotionService()
    
    # Get the emotion labels from the service
    emotion_labels = emotion_service.emotion_labels
    print(f"Loaded emotion service with {len(emotion_labels)} emotion labels")
    
    # Load test data
    texts, labels, label_cols = load_data(args.test_data)
    if texts is None or labels is None:
        print("Failed to load test data. Exiting.")
        return
    
    # Evaluate the service
    metrics = evaluate_with_emotion_service(
        emotion_service, 
        texts, 
        labels, 
        label_cols, 
        emotion_labels, 
        args.sample_size
    )
    
    # Print results
    print("\nBackend Emotion Service Evaluation Results:")
    print(f"Sample Size: {args.sample_size if args.sample_size else len(texts)}")
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print(f"F1 Score: {metrics['f1']:.4f}")
    print(f"Precision: {metrics['precision']:.4f}")
    print(f"Recall: {metrics['recall']:.4f}")
    
    # Save results
    if args.output:
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        with open(args.output, 'w') as f:
            json.dump(metrics, f, indent=2)
        print(f"Results saved to {args.output}")

if __name__ == "__main__":
    main()