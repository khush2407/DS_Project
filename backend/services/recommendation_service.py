from typing import Dict, List
import json
import os
from pathlib import Path

class RecommendationService:
    def __init__(self):
        self.activities = self._load_activities()
        self.emotion_mappings = self._create_emotion_mappings()
        self.difficulty_levels = ["beginner", "intermediate", "advanced"]
        self.time_requirements = ["short", "medium", "long"]

    def _load_activities(self) -> Dict:
        """Load wellness activities from JSON file."""
        activities = {
            "mindful_breathing": {
                "title": "Women's Mindful Breathing",
                "description": "A breathing technique designed for women to reduce stress and balance hormones",
                "duration": "5-10 minutes",
                "difficulty": "beginner",
                "benefits": ["Reduces stress", "Balances hormones", "Calms the mind", "Supports reproductive health"],
                "steps": [
                    "Find a quiet, comfortable place to sit",
                    "Place one hand on your chest and one on your abdomen",
                    "Breathe in slowly through your nose for 4 counts",
                    "Hold for 2 counts, focusing on feminine energy",
                    "Exhale slowly for 6 counts, releasing tension",
                    "Continue for 5-10 minutes"
                ]
            },
            "gratitude_journal": {
                "title": "Women's Gratitude Practice",
                "description": "A journaling practice designed to help women recognize their strengths and celebrate their achievements",
                "duration": "10-15 minutes",
                "difficulty": "beginner",
                "benefits": ["Boosts mood", "Increases self-worth", "Reduces anxiety", "Promotes female empowerment"],
                "steps": [
                    "Get a beautiful notebook that inspires you",
                    "Write down 3 things you're grateful for as a woman",
                    "Note one way you've shown strength today",
                    "Acknowledge one challenge you've overcome",
                    "Make this a daily practice to build self-confidence"
                ]
            },
            "body_scan": {
                "title": "Body Scan Meditation",
                "description": "Systematically scan your body for tension and release it",
                "duration": "15-20 minutes",
                "difficulty": "intermediate",
                "benefits": ["Reduces physical tension", "Improves body awareness", "Promotes relaxation"],
                "steps": [
                    "Lie down in a comfortable position",
                    "Start from your toes and move up to your head",
                    "Notice any tension in each body part",
                    "Breathe into tense areas and release"
                ]
            },
            "positive_affirmations": {
                "title": "Women's Empowerment Affirmations",
                "description": "Powerful affirmations specifically designed to help women overcome societal pressures and build confidence",
                "duration": "5 minutes",
                "difficulty": "beginner",
                "benefits": ["Builds self-esteem", "Challenges gender stereotypes", "Reduces negative self-talk", "Promotes female empowerment"],
                "steps": [
                    "Stand in front of a mirror in a confident pose",
                    "Choose 3-5 empowering statements like 'I am strong', 'My voice matters', 'I deserve respect'",
                    "Repeat each affirmation with conviction while maintaining eye contact with yourself",
                    "Place your hand over your heart as you speak to connect with your inner strength",
                    "Practice daily to build your confidence as a woman"
                ]
            },
            "emotional_release": {
                "title": "Emotional Release Exercise",
                "description": "Safe space to express and release strong emotions",
                "duration": "10-15 minutes",
                "difficulty": "intermediate",
                "benefits": ["Releases emotional tension", "Promotes emotional awareness", "Improves emotional regulation"],
                "steps": [
                    "Find a private, safe space",
                    "Identify the emotion you're feeling",
                    "Express it through movement, sound, or writing",
                    "Release and let go"
                ]
            },
            "self_compassion_meditation": {
                "title": "Self-Compassion Meditation",
                "description": "Practice being kind and understanding towards yourself",
                "duration": "10-15 minutes",
                "difficulty": "intermediate",
                "benefits": ["Reduces self-criticism", "Increases self-acceptance", "Promotes emotional healing"],
                "steps": [
                    "Find a quiet space",
                    "Focus on your breath",
                    "Repeat kind phrases to yourself",
                    "Feel the warmth of self-compassion"
                ]
            },
            "progressive_muscle_relaxation": {
                "title": "Progressive Muscle Relaxation",
                "description": "Systematically tense and relax different muscle groups to reduce physical tension",
                "duration": "15-20 minutes",
                "difficulty": "beginner",
                "benefits": ["Reduces muscle tension", "Improves sleep", "Decreases anxiety"],
                "steps": [
                    "Find a quiet space and lie down",
                    "Start with your toes, tense for 5 seconds",
                    "Release and relax for 10 seconds",
                    "Move up through each muscle group",
                    "End with your facial muscles"
                ]
            },
            "mindful_walking": {
                "title": "Mindful Walking",
                "description": "Practice walking meditation to connect with your body and surroundings",
                "duration": "10-15 minutes",
                "difficulty": "beginner",
                "benefits": ["Improves mindfulness", "Reduces stress", "Enhances body awareness"],
                "steps": [
                    "Find a quiet path or space",
                    "Walk slowly and deliberately",
                    "Focus on the sensation of each step",
                    "Notice your breath and surroundings",
                    "Maintain a steady, comfortable pace"
                ]
            },
            "emotional_journaling": {
                "title": "Emotional Journaling",
                "description": "Write about your feelings and experiences to process emotions",
                "duration": "15-20 minutes",
                "difficulty": "beginner",
                "benefits": ["Processes emotions", "Improves self-awareness", "Reduces stress"],
                "steps": [
                    "Find a quiet space with your journal",
                    "Write about your current emotions",
                    "Explore the triggers and thoughts",
                    "Reflect on possible solutions",
                    "End with positive affirmations"
                ]
            },
            "guided_visualization": {
                "title": "Guided Visualization",
                "description": "Use mental imagery to create a peaceful, positive state of mind",
                "duration": "10-15 minutes",
                "difficulty": "intermediate",
                "benefits": ["Reduces anxiety", "Improves mood", "Enhances creativity"],
                "steps": [
                    "Find a comfortable position",
                    "Close your eyes and breathe deeply",
                    "Imagine a peaceful scene",
                    "Engage all your senses in the visualization",
                    "Slowly return to the present moment"
                ]
            },
            "self_care_ritual": {
                "title": "Self-Care Ritual",
                "description": "Create a personalized self-care routine to nurture yourself",
                "duration": "20-30 minutes",
                "difficulty": "beginner",
                "benefits": ["Improves self-esteem", "Reduces stress", "Promotes well-being"],
                "steps": [
                    "Choose 2-3 self-care activities",
                    "Create a calming environment",
                    "Engage in each activity mindfully",
                    "Reflect on how you feel",
                    "Make it a regular practice"
                ]
            },
            "gratitude_meditation": {
                "title": "Gratitude Meditation",
                "description": "Focus on feelings of gratitude and appreciation",
                "duration": "10-15 minutes",
                "difficulty": "beginner",
                "benefits": ["Increases happiness", "Reduces stress", "Improves relationships"],
                "steps": [
                    "Find a quiet space",
                    "Focus on your breath",
                    "Think of something you're grateful for",
                    "Feel the gratitude in your body",
                    "Expand to more things you appreciate"
                ]
            },
            "emotional_release_art": {
                "title": "Emotional Release Art",
                "description": "Express emotions through creative art-making",
                "duration": "20-30 minutes",
                "difficulty": "beginner",
                "benefits": ["Processes emotions", "Reduces stress", "Enhances creativity"],
                "steps": [
                    "Gather art supplies",
                    "Choose colors that match your emotions",
                    "Create freely without judgment",
                    "Reflect on the process",
                    "Express what the art means to you"
                ]
            },
            "mindful_movement": {
                "title": "Mindful Movement",
                "description": "Practice gentle movement with awareness of body and breath",
                "duration": "15-20 minutes",
                "difficulty": "beginner",
                "benefits": ["Improves body awareness", "Reduces tension", "Enhances mindfulness"],
                "steps": [
                    "Find a quiet space",
                    "Start with gentle stretches",
                    "Move slowly and mindfully",
                    "Focus on breath and movement",
                    "End with relaxation"
                ]
            }
        }
        return activities

    def _create_emotion_mappings(self) -> Dict[str, List[str]]:
        """Create mappings between emotions and recommended activities."""
        return {
            "neutral": ["mindful_breathing", "gratitude_journal", "mindful_walking"],
            "approval": ["positive_affirmations", "gratitude_journal", "gratitude_meditation"],
            "admiration": ["gratitude_journal", "positive_affirmations", "self_care_ritual"],
            "annoyance": ["mindful_breathing", "emotional_release", "progressive_muscle_relaxation"],
            "gratitude": ["gratitude_journal", "positive_affirmations", "gratitude_meditation"],
            "disapproval": ["self_compassion_meditation", "mindful_breathing", "emotional_journaling"],
            "curiosity": ["mindful_breathing", "body_scan", "guided_visualization"],
            "amusement": ["positive_affirmations", "gratitude_journal", "mindful_movement"],
            "realization": ["mindful_breathing", "self_compassion_meditation", "emotional_journaling"],
            "optimism": ["positive_affirmations", "gratitude_journal", "guided_visualization"],
            "disappointment": ["self_compassion_meditation", "emotional_release", "emotional_journaling"],
            "love": ["gratitude_journal", "positive_affirmations", "self_care_ritual"],
            "anger": ["emotional_release", "mindful_breathing", "progressive_muscle_relaxation"],
            "joy": ["gratitude_journal", "positive_affirmations", "mindful_movement"],
            "confusion": ["mindful_breathing", "body_scan", "emotional_journaling"],
            "sadness": ["self_compassion_meditation", "emotional_release", "emotional_journaling"],
            "caring": ["gratitude_journal", "positive_affirmations", "self_care_ritual"],
            "excitement": ["mindful_breathing", "body_scan", "mindful_movement"],
            "surprise": ["mindful_breathing", "gratitude_journal", "guided_visualization"],
            "disgust": ["emotional_release", "mindful_breathing", "progressive_muscle_relaxation"],
            "desire": ["mindful_breathing", "body_scan", "guided_visualization"],
            "fear": ["mindful_breathing", "self_compassion_meditation", "progressive_muscle_relaxation"],
            "remorse": ["self_compassion_meditation", "emotional_release", "emotional_journaling"],
            "embarrassment": ["self_compassion_meditation", "positive_affirmations", "emotional_journaling"],
            "nervousness": ["mindful_breathing", "body_scan", "progressive_muscle_relaxation"],
            "pride": ["positive_affirmations", "gratitude_journal", "self_care_ritual"],
            "relief": ["mindful_breathing", "gratitude_journal", "progressive_muscle_relaxation"],
            "grief": ["self_compassion_meditation", "emotional_release", "emotional_journaling"]
        }

    def get_recommendations(self, emotions: Dict[str, float], primary_emotion: str, user_preferences=None) -> List[Dict]:
        """
        Get personalized recommendations based on detected emotions.
        Returns a list of recommended activities with their details.
        """
        try:
            # Get activities for primary emotion
            recommended_activity_ids = self.emotion_mappings.get(primary_emotion, [])
            
            # If no activities found for the primary emotion, use a default set
            if not recommended_activity_ids:
                print(f"No activities found for emotion: {primary_emotion}, using defaults")
                recommended_activity_ids = ["mindful_breathing", "gratitude_journal", "self_compassion_meditation"]
            
            # Get activity details
            recommendations = []
            for activity_id in recommended_activity_ids:
                if activity_id in self.activities:
                    activity = self.activities[activity_id].copy()
                    recommendations.append(activity)
                else:
                    print(f"Activity ID not found: {activity_id}")
            
            # If no valid activities found, provide default recommendations
            if not recommendations:
                print("No valid activities found, using default recommendations")
                default_ids = ["mindful_breathing", "gratitude_journal"]
                recommendations = [self.activities[id].copy() for id in default_ids if id in self.activities]
                
                # If still no recommendations, create a basic one
                if not recommendations:
                    recommendations = [{
                        "title": "Deep Breathing Exercise",
                        "description": "A simple breathing technique to help calm your mind and reduce stress.",
                        "duration": "5 minutes",
                        "difficulty": "beginner",
                        "benefits": ["Reduces stress", "Improves focus", "Calms the mind"],
                        "steps": [
                            "Find a comfortable seated position",
                            "Close your eyes and breathe naturally",
                            "Inhale deeply through your nose for 4 counts",
                            "Hold your breath for 2 counts",
                            "Exhale slowly through your mouth for 6 counts",
                            "Repeat for 5 minutes"
                        ]
                    }]

            # Add emotional context to recommendations
            for rec in recommendations:
                try:
                    rec['emotional_context'] = self._get_emotional_context(primary_emotion, emotions)
                except Exception as context_error:
                    print(f"Error adding emotional context: {context_error}")
                    rec['emotional_context'] = "These activities are designed to support your emotional wellbeing."

            return recommendations

        except Exception as e:
            print(f"Error generating recommendations: {str(e)}")
            # Return default recommendations instead of raising an exception
            default_recommendations = [{
                "title": "Deep Breathing Exercise",
                "description": "A simple breathing technique to help calm your mind and reduce stress.",
                "duration": "5 minutes",
                "difficulty": "beginner",
                "benefits": ["Reduces stress", "Improves focus", "Calms the mind"],
                "steps": [
                    "Find a comfortable seated position",
                    "Close your eyes and breathe naturally",
                    "Inhale deeply through your nose for 4 counts",
                    "Hold your breath for 2 counts",
                    "Exhale slowly through your mouth for 6 counts",
                    "Repeat for 5 minutes"
                ],
                "emotional_context": "This exercise helps with any emotional state"
            }]
            return default_recommendations

    def _get_emotional_context(self, primary_emotion: str, emotions: Dict[str, float]) -> str:
        """Generate emotional context for recommendations tailored for women."""
        try:
            confidence = emotions.get(primary_emotion, 0) * 100
            
            # Safely get secondary emotions
            secondary_emotions = []
            try:
                secondary_emotions = sorted(
                    [(e, s) for e, s in emotions.items() if e != primary_emotion],
                    key=lambda x: x[1],
                    reverse=True
                )[:2]
            except Exception:
                # If sorting fails, just use an empty list
                pass

            women_focused_intros = [
                "As a woman navigating today's world, your emotional wellbeing is essential.",
                "Women often experience emotions differently due to unique biological and social factors.",
                "Your emotional health as a woman deserves special attention and care.",
                "The challenges women face can create complex emotional responses that need nurturing."
            ]
            
            import random
            intro = random.choice(women_focused_intros)
            
            context = f"{intro} Based on your emotional state showing {primary_emotion} ({confidence:.1f}% confidence)"
            if secondary_emotions:
                context += f" with elements of {', '.join([e for e, _ in secondary_emotions])}"
            context += ", these women-centered activities are recommended to support your emotional wellness and empowerment."

            return context
        except Exception as e:
            print(f"Error generating emotional context: {str(e)}")
            return "These activities are designed to support your emotional wellbeing and empowerment."

    def get_explanation(self, emotions: Dict[str, float], primary_emotion: str) -> str:
        """Generate a women-focused explanation for the recommendations."""
        try:
            confidence = emotions.get(primary_emotion, 0) * 100
            return (
                f"As a woman experiencing {primary_emotion} "
                f"with {confidence:.1f}% confidence, we've selected these activities "
                "specifically designed for women's emotional needs. Each activity considers "
                "the unique challenges women face and provides supportive practices to "
                "nurture your wellbeing, honor your feminine wisdom, and strengthen your "
                "emotional resilience in a world that often overlooks women's experiences."
            )
        except Exception as e:
            print(f"Error generating explanation: {str(e)}")
            return (
                "We've selected these activities specifically designed for women's emotional needs. "
                "Each activity provides supportive practices to nurture your wellbeing and "
                "strengthen your emotional resilience."
            )
        
    def get_all_activities(self) -> List[Dict]:
        """Get all available activities with their IDs."""
        activities_with_ids = []
        for activity_id, activity in self.activities.items():
            activity_with_id = activity.copy()
            activity_with_id['id'] = activity_id
            activities_with_ids.append(activity_with_id)
        return activities_with_ids
        
    def get_activity(self, activity_id: str) -> Dict:
        """Get a specific activity by ID."""
        if activity_id in self.activities:
            activity = self.activities[activity_id].copy()
            activity['id'] = activity_id
            return activity
        return None