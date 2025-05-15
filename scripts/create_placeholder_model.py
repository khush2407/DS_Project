import torch
from transformers import AutoModelForSequenceClassification
import pickle
import os
from pathlib import Path

# Create directories if they don't exist
os.makedirs("data/processed", exist_ok=True)

# Define emotion labels
emotion_labels = [
    "neutral", "approval", "admiration", "annoyance", "gratitude",
    "disapproval", "curiosity", "amusement", "realization", "optimism",
    "disappointment", "love", "anger", "joy", "confusion", "sadness",
    "caring", "excitement", "surprise", "disgust", "desire", "fear",
    "remorse", "embarrassment", "nervousness", "pride", "relief", "grief"
]

# Load base model
print("Loading base model...")
model_name = "distilbert-base-uncased"
model = AutoModelForSequenceClassification.from_pretrained(
    model_name,
    num_labels=len(emotion_labels)
)

# Create a placeholder trained model by slightly modifying the base model weights
# This simulates a trained model without actually training it
print("Creating placeholder trained model...")
for param in model.parameters():
    # Add small random values to the parameters to simulate training
    param.data = param.data + 0.01 * torch.randn_like(param.data)

# Save the model state dictionary
print("Saving the placeholder model...")
model_path = Path("data/processed/emotion_model.pkl")
with open(model_path, 'wb') as f:
    pickle.dump(model.state_dict(), f)

print(f"Placeholder model saved to {model_path}")
print("Note: This is a placeholder model for demonstration purposes only.")
print("For production use, replace with a properly trained model using train_emotion_model.py")