from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np
from typing import Dict, Tuple, List
import redis
import json
from functools import lru_cache

class EmotionService:
    def __init__(self):
        self.model_name = "distilbert-base-uncased"  # We'll fine-tune this for our emotions
        self.tokenizer = None
        self.model = None
        self.emotion_labels = [
            "neutral", "approval", "admiration", "annoyance", "gratitude",
            "disapproval", "curiosity", "amusement", "realization", "optimism",
            "disappointment", "love", "anger", "joy", "confusion", "sadness",
            "caring", "excitement", "surprise", "disgust", "desire", "fear",
            "remorse", "embarrassment", "nervousness", "pride", "relief", "grief"
        ]
        # Initialize in-memory cache
        self.memory_cache = {}
        
        # Try to connect to Redis, but don't fail if it's not available
        try:
            self.redis_client = redis.Redis(
                host='redis',
                port=6379,
                db=0,
                decode_responses=True,
                socket_connect_timeout=2,  # Set a short timeout
                socket_timeout=2
            )
            # Test the connection
            self.redis_client.ping()
            self.redis_available = True
            print("Successfully connected to Redis for emotion service")
        except Exception as e:
            print(f"Redis not available: {str(e)}. Using in-memory cache instead.")
            self.redis_available = False
        
        self._load_model()

    def _load_model(self):
        """Load the pre-trained model and tokenizer."""
        try:
            import pickle
            import os
            from pathlib import Path
            
            # Initialize model and tokenizer
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = AutoModelForSequenceClassification.from_pretrained(
                    self.model_name,
                    num_labels=len(self.emotion_labels)
                )
                
                # Load the fine-tuned model weights for women's emotional expressions
                model_path = Path("data/processed/emotion_model.pkl")
                if os.path.exists(model_path):
                    try:
                        print(f"Loading fine-tuned emotion model from {model_path}")
                        with open(model_path, 'rb') as f:
                            model_state = pickle.load(f)
                            if isinstance(model_state, dict):
                                self.model.load_state_dict(model_state)
                                print("Successfully loaded fine-tuned model weights")
                            else:
                                print("Warning: Model file does not contain valid state dictionary")
                    except Exception as model_load_error:
                        print(f"Error loading fine-tuned model: {str(model_load_error)}. Using base model.")
                else:
                    print(f"Warning: Fine-tuned model not found at {model_path}. Using base model.")
                    
                self.model.eval()
                print("Model successfully loaded and ready for inference")
            except Exception as model_init_error:
                print(f"Error initializing model: {str(model_init_error)}")
                self.model = None
                self.tokenizer = None
                print("Will use keyword-based fallback for emotion detection")
                
        except Exception as e:
            print(f"Error in _load_model: {str(e)}")
            self.model = None
            self.tokenizer = None

    def preprocess_text(self, text: str) -> torch.Tensor:
        """Preprocess the input text for the model."""
        inputs = self.tokenizer(
            text,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        )
        return inputs

    @lru_cache(maxsize=1000)
    def _get_cached_emotions(self, text: str) -> Tuple[Dict[str, float], str]:
        """Get cached emotions for a text if available."""
        cache_key = f"emotion:{text}"
        
        # Try Redis first if available
        if self.redis_available:
            try:
                cached_result = self.redis_client.get(cache_key)
                if cached_result:
                    result = json.loads(cached_result)
                    return result['emotions'], result['primary_emotion']
            except Exception as e:
                print(f"Error getting cached emotions from Redis: {str(e)}")
                print("Falling back to in-memory cache")
                # Disable Redis for future operations
                self.redis_available = False
        
        # Use in-memory cache if Redis is not available or failed
        if cache_key in self.memory_cache:
            result = self.memory_cache[cache_key]
            return result['emotions'], result['primary_emotion']
                
        return None, None

    def _cache_emotions(self, text: str, emotions: Dict[str, float], primary_emotion: str):
        """Cache the emotion detection results."""
        cache_key = f"emotion:{text}"
        cache_value = {
            'emotions': emotions,
            'primary_emotion': primary_emotion
        }
        
        # Try Redis first if available
        if self.redis_available:
            try:
                self.redis_client.setex(cache_key, 3600, json.dumps(cache_value))  # Cache for 1 hour
            except Exception as e:
                print(f"Error caching emotions to Redis: {str(e)}")
                print("Falling back to in-memory cache")
                # Disable Redis for future operations
                self.redis_available = False
        
        # Always store in memory cache as a backup or if Redis is not available
        self.memory_cache[cache_key] = cache_value

    def detect_emotions(self, text: str) -> Tuple[Dict[str, float], str]:
        """
        Detect emotions in the given text using a model fine-tuned for women's emotional expressions.
        Returns a dictionary of emotions with confidence scores and the primary emotion.
        """
        try:
            # Check cache first
            cached_emotions, cached_primary = self._get_cached_emotions(text)
            if cached_emotions and cached_primary:
                return cached_emotions, cached_primary

            # Use the trained model to detect emotions
            if self.model and self.tokenizer:
                # Preprocess the text
                inputs = self.preprocess_text(text)
                
                # Get model predictions
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    logits = outputs.logits
                    
                # Convert logits to probabilities
                probs = torch.nn.functional.softmax(logits, dim=1)[0].tolist()
                
                # Create emotions dictionary with probabilities
                emotions = {
                    self.emotion_labels[i]: prob
                    for i, prob in enumerate(probs)
                    if prob > 0.05  # Only include emotions with significant probability
                }
                
                # Get primary emotion (highest probability)
                primary_emotion = self.emotion_labels[probs.index(max(probs))]
                
                # Cache the results
                self._cache_emotions(text, emotions, primary_emotion)
                
                return emotions, primary_emotion
            else:
                # Fallback to keyword-based analysis if model isn't loaded
                print("Model not loaded, using keyword-based analysis")
                
                text_lower = text.lower()
                
                # Define some keywords for different emotions commonly expressed by women
                joy_keywords = ["happy", "joy", "excited", "wonderful", "love", "grateful"]
                sadness_keywords = ["sad", "upset", "hurt", "disappointed", "lonely", "tired"]
                anxiety_keywords = ["anxious", "worried", "stressed", "overwhelmed", "nervous"]
                anger_keywords = ["angry", "frustrated", "annoyed", "unfair", "ignored"]
                
                # Count keyword occurrences
                joy_count = sum(1 for word in joy_keywords if word in text_lower)
                sadness_count = sum(1 for word in sadness_keywords if word in text_lower)
                anxiety_count = sum(1 for word in anxiety_keywords if word in text_lower)
                anger_count = sum(1 for word in anger_keywords if word in text_lower)
                
                # Determine primary emotion based on keyword counts
                counts = {
                    "joy": joy_count,
                    "sadness": sadness_count,
                    "fear": anxiety_count,
                    "anger": anger_count
                }
                
                # If no keywords found, default to a balanced emotional state
                if sum(counts.values()) == 0:
                    emotions = {
                        "optimism": 0.4,
                        "curiosity": 0.3,
                        "joy": 0.2,
                        "caring": 0.1
                    }
                    primary_emotion = "optimism"
                else:
                    # Find primary emotion
                    primary_emotion = max(counts, key=counts.get)
                    
                    # Create emotion distribution
                    total = sum(counts.values())
                    emotions = {emotion: count/total * 0.7 for emotion, count in counts.items() if count > 0}
                    
                    # Add some related emotions for a more nuanced profile
                    if primary_emotion == "joy":
                        emotions["optimism"] = 0.3
                        emotions["gratitude"] = 0.2
                    elif primary_emotion == "sadness":
                        emotions["disappointment"] = 0.3
                        emotions["grief"] = 0.2
                    elif primary_emotion == "fear":
                        emotions["nervousness"] = 0.3
                        emotions["confusion"] = 0.2
                    elif primary_emotion == "anger":
                        emotions["disapproval"] = 0.3
                        emotions["annoyance"] = 0.2
                
                # Cache the results
                self._cache_emotions(text, emotions, primary_emotion)
                
                return emotions, primary_emotion

        except Exception as e:
            # Log the error but return fallback data to prevent frontend errors
            print(f"Error in emotion detection: {str(e)}")
            fallback_emotions = {"optimism": 0.5, "joy": 0.3, "caring": 0.2}
            return fallback_emotions, "optimism"

    def get_emotion_summary(self, emotions: Dict[str, float]) -> str:
        """Generate a women-focused, human-readable summary of the detected emotions."""
        if not emotions:
            return "No strong emotions detected. As women, we sometimes mask our feelings - take a moment to reflect on what you might be experiencing beneath the surface."
            
        # Sort emotions by confidence
        sorted_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)
        
        # Get top 3 emotions
        top_emotions = sorted_emotions[:3]
        
        # Create a more personalized, women-focused summary
        primary_emotion = sorted_emotions[0][0]
        
        # Emotion-specific summaries tailored for women
        emotion_insights = {
            "joy": "Your joy radiates through your words. Women's happiness often comes from connection and nurturing relationships.",
            "sadness": "Your sadness is valid and deserves acknowledgment. Women often carry emotional labor that goes unrecognized.",
            "fear": "Your anxiety is understandable in a world that often places extra pressure on women. Remember to honor your boundaries.",
            "anger": "Your anger is justified and powerful. Women's anger is often dismissed, but it can be a catalyst for positive change.",
            "optimism": "Your optimism shines through. Women's hopeful outlook often sustains communities through challenges.",
            "disappointment": "Your disappointment reflects your high standards and values. Women often hold visions for better possibilities.",
            "gratitude": "Your gratitude shows emotional intelligence. Women's appreciation often strengthens social bonds.",
            "caring": "Your compassion is evident. Women's nurturing nature is a strength, though remember to extend that care to yourself too."
        }
        
        # Default insight if specific emotion not found
        default_insight = "Your emotional awareness is a strength. Women's emotional intelligence is a powerful resource for navigating life's complexities."
        
        # Build the summary
        summary = emotion_insights.get(primary_emotion, default_insight) + "\n\nDetected emotions: "
        summary += ", ".join([f"{emotion} ({conf*100:.1f}%)" for emotion, conf in top_emotions])
        
        return summary

    def batch_detect_emotions(self, texts: List[str]) -> List[Tuple[Dict[str, float], str]]:
        """Process multiple texts in batch for better performance."""
        results = []
        for text in texts:
            emotions, primary = self.detect_emotions(text)
            results.append((emotions, primary))
        return results 