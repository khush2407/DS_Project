import pickle
import os
from pathlib import Path
import random

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

# Create a simple dictionary to simulate a model state dictionary
# This will be a valid pickle file that can be loaded by the emotion_service.py
print("Creating simple model state dictionary...")
model_state = {}

# Add some random parameters to simulate a model state dictionary
for i in range(10):
    param_name = f"layer_{i}.weight"
    # Create a small random array
    param_value = [[random.random() for _ in range(5)] for _ in range(5)]
    model_state[param_name] = param_value

    param_name = f"layer_{i}.bias"
    param_value = [random.random() for _ in range(5)]
    model_state[param_name] = param_value

# Save the model state dictionary
print("Saving the simple model...")
model_path = Path("data/processed/emotion_model.pkl")
with open(model_path, 'wb') as f:
    pickle.dump(model_state, f)

print(f"Simple model saved to {model_path}")
print("Note: This is a simple model for demonstration purposes only.")
print("For production use, replace with a properly trained model using train_emotion_model.py")