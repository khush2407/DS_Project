import streamlit as st
import torch
import pickle
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Define emotion labels
emotion_labels = [
    "neutral", "approval", "admiration", "annoyance", "gratitude",
    "disapproval", "curiosity", "amusement", "realization", "optimism",
    "disappointment", "love", "anger", "joy", "confusion", "sadness",
    "caring", "excitement", "surprise", "disgust", "desire", "fear",
    "remorse", "embarrassment", "nervousness", "pride", "relief", "grief"
]

class EmotionModel:
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
                    st.info(f"Loading full model from {self.full_model_path}")
                    self.model = AutoModelForSequenceClassification.from_pretrained(
                        self.full_model_path
                    )
                    st.success("Successfully loaded full model")
                except Exception as e:
                    st.warning(f"Error loading full model: {e}")
                    st.info("Falling back to state dict loading")
                    self._load_from_state_dict()
            else:
                self._load_from_state_dict()
            
            # Move model to device
            if self.model:
                self.model.to(self.device)
                self.model.eval()
                st.success(f"Model loaded and ready for inference on {self.device}")
            
        except Exception as e:
            st.error(f"Error in _load_model: {e}")
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
                    st.info(f"Loading fine-tuned model from {model_path}")
                    with open(model_path, 'rb') as f:
                        model_state = pickle.load(f)
                        if isinstance(model_state, dict):
                            self.model.load_state_dict(model_state)
                            st.success("Successfully loaded fine-tuned model weights")
                        else:
                            st.warning("Model file does not contain valid state dictionary")
                except Exception as e:
                    st.warning(f"Error loading fine-tuned model: {e}")
                    st.info("Using base model instead")
            else:
                st.warning(f"Model file not found at {model_path}. Using base model.")
        except Exception as e:
            st.error(f"Error in _load_from_state_dict: {e}")
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
            st.error("Model or tokenizer not loaded properly")
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

def plot_emotions(emotions):
    """Plot emotions as a bar chart."""
    # Sort emotions by value
    sorted_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)
    labels, values = zip(*sorted_emotions[:10])  # Show top 10 emotions
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(labels, values, color='skyblue')
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{height:.2f}', ha='center', va='bottom')
    
    plt.title('Emotion Probabilities')
    plt.xlabel('Emotions')
    plt.ylabel('Probability')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    return fig

def get_emotion_summary(primary_emotion, emotions):
    """Generate a summary based on the detected emotions."""
    # Emotion-specific summaries
    emotion_insights = {
        "joy": "Your joy radiates through your words. This positive emotion is associated with happiness, satisfaction, and pleasure.",
        "sadness": "Your sadness is reflected in your words. This emotion often arises from loss, disappointment, or feeling down.",
        "fear": "Your text suggests feelings of fear or anxiety. This emotion is a response to perceived threats or uncertainty.",
        "anger": "Your words express anger. This emotion often stems from feeling wronged, frustrated, or threatened.",
        "optimism": "Your text conveys optimism. This forward-looking emotion focuses on positive outcomes and possibilities.",
        "disappointment": "Your words suggest disappointment. This emotion often follows unmet expectations or hopes.",
        "gratitude": "Your text expresses gratitude. This emotion acknowledges appreciation for something or someone.",
        "caring": "Your words show caring and compassion. This emotion reflects concern for others' wellbeing."
    }
    
    # Default insight if specific emotion not found
    default_insight = "Your text shows a complex emotional state. Emotions are nuanced and can be influenced by many factors."
    
    # Build the summary
    summary = emotion_insights.get(primary_emotion, default_insight)
    
    return summary

def main():
    st.set_page_config(
        page_title="Emotion Detection Model",
        page_icon="😊",
        layout="wide"
    )
    
    st.title("Emotion Detection Model")
    st.write("This application uses a fine-tuned DistilBERT model to detect emotions in text.")
    
    # Sidebar for model selection
    st.sidebar.header("Model Settings")
    model_path = st.sidebar.text_input(
        "Model State Dict Path",
        value="data/processed/emotion_model.pkl"
    )
    full_model_path = st.sidebar.text_input(
        "Full Model Path",
        value="models/emotion_detector"
    )
    
    # Initialize model
    with st.spinner("Loading model..."):
        model = EmotionModel(model_path, full_model_path)
    
    # Text input
    st.header("Enter Text")
    text_input = st.text_area(
        "Enter text to analyze",
        height=150,
        placeholder="Type your text here..."
    )
    
    # Sample texts
    st.subheader("Or try a sample:")
    sample_texts = {
        "Happy": "I'm feeling so happy today! Everything is going well and I'm excited about the future.",
        "Sad": "I'm feeling really down today. Nothing seems to be going right and I miss my friends.",
        "Angry": "I can't believe they did that! It's so frustrating and unfair. I'm really upset about it.",
        "Anxious": "I'm worried about my upcoming presentation. What if I mess up? I can't stop thinking about it.",
        "Surprised": "Wow! I didn't expect that at all. This is such an unexpected turn of events."
    }
    
    cols = st.columns(len(sample_texts))
    for i, (emotion, text) in enumerate(sample_texts.items()):
        if cols[i].button(emotion):
            text_input = text
            st.session_state.text_input = text
    
    # Store text input in session state
    if 'text_input' not in st.session_state:
        st.session_state.text_input = text_input
    elif text_input != st.session_state.text_input:
        st.session_state.text_input = text_input
    
    # Analyze button
    if st.button("Analyze Emotions") or st.session_state.text_input:
        if not st.session_state.text_input:
            st.warning("Please enter some text to analyze.")
        else:
            with st.spinner("Analyzing emotions..."):
                emotions, primary_emotion = model.predict(st.session_state.text_input)
            
            if emotions and primary_emotion:
                # Display results
                st.header("Analysis Results")
                
                # Two columns layout
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.subheader("Primary Emotion")
                    st.markdown(f"### {primary_emotion.capitalize()}")
                    
                    st.subheader("Emotion Summary")
                    st.write(get_emotion_summary(primary_emotion, emotions))
                    
                    st.subheader("Top Emotions")
                    for emotion, prob in list(emotions.items())[:5]:
                        st.write(f"**{emotion.capitalize()}**: {prob:.4f}")
                
                with col2:
                    st.subheader("Emotion Distribution")
                    fig = plot_emotions(emotions)
                    st.pyplot(fig)
            else:
                st.error("Failed to analyze emotions. Please try again.")

if __name__ == "__main__":
    main()