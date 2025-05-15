import pandas as pd
import numpy as np
import os
import pickle
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multioutput import MultiOutputClassifier
import argparse
from tqdm import tqdm

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
            return None, None
        
        print(f"Using {len(label_cols)} columns as labels: {label_cols[:5]}...")
        labels = df[label_cols].values
        
        return texts, labels
    
    except Exception as e:
        print(f"Error loading data: {e}")
        return None, None

def train_simple_model(train_texts, train_labels, test_texts, test_labels):
    """Train a simple TF-IDF + Logistic Regression model and evaluate it."""
    print("Training a simple TF-IDF + Logistic Regression model...")
    
    # Create TF-IDF features
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
    X_train = vectorizer.fit_transform(train_texts)
    X_test = vectorizer.transform(test_texts)
    
    # Train a logistic regression model
    model = MultiOutputClassifier(LogisticRegression(max_iter=1000))
    model.fit(X_train, train_labels)
    
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Calculate metrics
    accuracy = accuracy_score(test_labels, y_pred)
    f1 = f1_score(test_labels, y_pred, average='weighted', zero_division=0)
    precision = precision_score(test_labels, y_pred, average='weighted', zero_division=0)
    recall = recall_score(test_labels, y_pred, average='weighted', zero_division=0)
    
    return {
        "accuracy": accuracy,
        "f1": f1,
        "precision": precision,
        "recall": recall
    }

def main():
    parser = argparse.ArgumentParser(description="Run a simple accuracy test using TF-IDF + Logistic Regression")
    parser.add_argument("--train_data", type=str, default="data/processed/train.pkl",
                        help="Path to the training data")
    parser.add_argument("--test_data", type=str, default="data/processed/test.pkl",
                        help="Path to the test data")
    parser.add_argument("--sample_size", type=int, default=None,
                        help="Number of examples to sample for training (default: use all)")
    args = parser.parse_args()
    
    # Load training data
    train_texts, train_labels = load_data(args.train_data)
    if train_texts is None or train_labels is None:
        print("Failed to load training data. Exiting.")
        return
    
    # Load test data
    test_texts, test_labels = load_data(args.test_data)
    if test_texts is None or test_labels is None:
        print("Failed to load test data. Exiting.")
        return
    
    # Sample data if requested
    if args.sample_size and args.sample_size < len(train_texts):
        indices = np.random.choice(len(train_texts), args.sample_size, replace=False)
        train_texts = [train_texts[i] for i in indices]
        train_labels = train_labels[indices]
        print(f"Sampled {args.sample_size} examples for training")
    
    # Train and evaluate model
    metrics = train_simple_model(train_texts, train_labels, test_texts, test_labels)
    
    # Print results
    print("\nSimple Model Accuracy Test Results:")
    print(f"Training examples: {len(train_texts)}")
    print(f"Test examples: {len(test_texts)}")
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print(f"F1 Score: {metrics['f1']:.4f}")
    print(f"Precision: {metrics['precision']:.4f}")
    print(f"Recall: {metrics['recall']:.4f}")

if __name__ == "__main__":
    main()