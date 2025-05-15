import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import pickle
import os
import json
import numpy as np
import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

# Define emotion labels
emotion_labels = [
    "neutral", "approval", "admiration", "annoyance", "gratitude",
    "disapproval", "curiosity", "amusement", "realization", "optimism",
    "disappointment", "love", "anger", "joy", "confusion", "sadness",
    "caring", "excitement", "surprise", "disgust", "desire", "fear",
    "remorse", "embarrassment", "nervousness", "pride", "relief", "grief"
]

class EmotionInference:
    def __init__(self, model_path=None, full_model_path=None):
        self.model_name = "distilbert-base-uncased"
        self.model_path = model_path or "data/processed/emotion_model.pkl"
        self.full_model_path = full_model_path or "models/emotion_detector"
        self.tokenizer = None
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        self._load_model()
    
    def _load_model(self):
        """Load the pre-trained model and tokenizer."""
        try:
            # Initialize tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            # Try loading from full model path first
            if os.path.exists(self.full_model_path):
                try:
                    print(f"Loading full model from {self.full_model_path}")
                    self.model = AutoModelForSequenceClassification.from_pretrained(
                        self.full_model_path
                    )
                    print("Successfully loaded full model")
                except Exception as e:
                    print(f"Error loading full model: {e}")
                    print("Falling back to state dict loading")
                    self._load_from_state_dict()
            else:
                self._load_from_state_dict()
            
            # Move model to device
            if self.model:
                self.model.to(self.device)
                self.model.eval()
                print(f"Model loaded and ready for inference on {self.device}")
            
        except Exception as e:
            print(f"Error in _load_model: {e}")
            self.model = None
            self.tokenizer = None
    
    def _load_from_state_dict(self):
        """Load model from state dictionary."""
        try:
            # Initialize model
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.model_name,
                num_labels=len(emotion_labels),
                problem_type="multi_label_classification"
            )
            
            # Load state dict if available
            model_path = Path(self.model_path)
            if os.path.exists(model_path):
                try:
                    print(f"Loading fine-tuned model from {model_path}")
                    with open(model_path, 'rb') as f:
                        model_state = pickle.load(f)
                        if isinstance(model_state, dict):
                            self.model.load_state_dict(model_state)
                            print("Successfully loaded fine-tuned model weights")
                        else:
                            print("Warning: Model file does not contain valid state dictionary")
                except Exception as e:
                    print(f"Error loading fine-tuned model: {e}")
                    print("Using base model instead")
            else:
                print(f"Model file not found at {model_path}. Using base model.")
        except Exception as e:
            print(f"Error in _load_from_state_dict: {e}")
            self.model = None
    
    def preprocess_text(self, text):
        """Preprocess the input text for the model."""
        inputs = self.tokenizer(
            text,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        )
        return inputs
    
    def predict(self, text):
        """Predict emotions for the given text."""
        if not self.model or not self.tokenizer:
            print("Model or tokenizer not loaded properly")
            return None, None
        
        # Preprocess text
        inputs = self.preprocess_text(text)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Get predictions
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
        
        # Convert logits to probabilities
        probs = torch.sigmoid(logits)[0].cpu().numpy()
        
        # Create emotions dictionary with probabilities
        emotions = {
            emotion_labels[i]: float(prob)
            for i, prob in enumerate(probs)
            if prob > 0.05  # Only include emotions with significant probability
        }
        
        # Sort emotions by probability
        emotions = dict(sorted(emotions.items(), key=lambda x: x[1], reverse=True))
        
        # Get primary emotion (highest probability)
        primary_emotion = emotion_labels[np.argmax(probs)]
        
        return emotions, primary_emotion
    
    def plot_emotions(self, emotions, output_path=None):
        """Plot emotions as a bar chart."""
        # Sort emotions by value
        sorted_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)
        labels, values = zip(*sorted_emotions[:10])  # Show top 10 emotions
        
        plt.figure(figsize=(12, 6))
        bars = plt.bar(labels, values, color='skyblue')
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{height:.2f}', ha='center', va='bottom')
        
        plt.title('Emotion Probabilities')
        plt.xlabel('Emotions')
        plt.ylabel('Probability')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path)
            print(f"Plot saved to {output_path}")
        else:
            plt.show()
        
        plt.close()

def main():
    parser = argparse.ArgumentParser(description="Run emotion inference on text")
    parser.add_argument("--text", type=str, help="Text to analyze")
    parser.add_argument("--file", type=str, help="File containing text to analyze")
    parser.add_argument("--model_path", type=str, help="Path to model state dict")
    parser.add_argument("--full_model_path", type=str, help="Path to full model directory")
    parser.add_argument("--output", type=str, help="Output directory for plots")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    args = parser.parse_args()
    
    # Create output directory if specified
    if args.output:
        os.makedirs(args.output, exist_ok=True)
    
    # Initialize inference
    inference = EmotionInference(
        model_path=args.model_path,
        full_model_path=args.full_model_path
    )
    
    if args.interactive:
        print("\nEmotion Analysis Interactive Mode")
        print("Type 'exit' to quit\n")
        
        while True:
            text = input("Enter text to analyze: ")
            if text.lower() == 'exit':
                break
            
            emotions, primary_emotion = inference.predict(text)
            
            print(f"\nPrimary emotion: {primary_emotion}")
            print("\nTop emotions:")
            for emotion, prob in list(emotions.items())[:5]:
                print(f"  {emotion}: {prob:.4f}")
            
            # Plot emotions
            inference.plot_emotions(emotions)
            
            print("\n" + "-"*50 + "\n")
    
    elif args.text:
        # Process single text
        emotions, primary_emotion = inference.predict(args.text)
        
        print(f"\nText: {args.text}")
        print(f"Primary emotion: {primary_emotion}")
        print("\nTop emotions:")
        for emotion, prob in list(emotions.items())[:5]:
            print(f"  {emotion}: {prob:.4f}")
        
        # Plot emotions
        if args.output:
            plot_path = os.path.join(args.output, "emotion_plot.png")
            inference.plot_emotions(emotions, plot_path)
        else:
            inference.plot_emotions(emotions)
    
    elif args.file:
        # Process text from file
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read()
            
            emotions, primary_emotion = inference.predict(text)
            
            print(f"\nAnalyzed text from: {args.file}")
            print(f"Primary emotion: {primary_emotion}")
            print("\nTop emotions:")
            for emotion, prob in list(emotions.items())[:5]:
                print(f"  {emotion}: {prob:.4f}")
            
            # Plot emotions
            if args.output:
                plot_path = os.path.join(args.output, "emotion_plot.png")
                inference.plot_emotions(emotions, plot_path)
            else:
                inference.plot_emotions(emotions)
        
        except Exception as e:
            print(f"Error reading file: {e}")
    
    else:
        print("Please provide text to analyze using --text or --file, or use --interactive mode")
        parser.print_help()

if __name__ == "__main__":
    main()