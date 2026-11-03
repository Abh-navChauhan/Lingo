"""
ADAPTIVE LEARNING RECOMMENDATION POLICY ENGINE
----------------------------------------------
Statistical Machine Learning (SML) College Project - Duolingo Adaptive Learning Platform

This engine implements the documented pedagogical recommendation policy:
1. Low predicted mastery / struggle -> Bite-sized foundational revision, difficulty down-scaling.
2. Intermediate mastery -> Targeted reinforcement on identified weak topics.
3. High predicted mastery -> Accelerated challenge modules, difficulty up-scaling.
4. Identifies strongest and weakest learning topics based on historical accuracy records.
"""

from typing import Dict, List, Any

DIFFICULTY_LEVELS = {
    "Beginner": "FOUNDATION (Bite-sized vocabulary & multiple choice)",
    "Intermediate": "STANDARD (Mixed translation, sentence composition, listening)",
    "Advanced": "MASTERY (Complex syntax, timed rapid-fire challenge)"
}

def generate_recommendations(
    predicted_mastery: str,
    confidence: float,
    current_topic: str,
    topic_history: Dict[str, float] = None,
    recent_accuracy: float = 0.8,
    avg_response_time: float = 15.0
) -> Dict[str, Any]:
    """
    Executes adaptive policy mapping ML predicted mastery and cognitive latency
    into personalized next-action recommendations.
    """
    if topic_history is None or len(topic_history) == 0:
        topic_history = {current_topic: recent_accuracy}
        
    # Rank topics by historical mastery
    sorted_topics = sorted(topic_history.items(), key=lambda item: item[1])
    weakest_topic = sorted_topics[0][0]
    weakest_score = round(float(sorted_topics[0][1]), 2)
    strongest_topic = sorted_topics[-1][0]
    strongest_score = round(float(sorted_topics[-1][1]), 2)
    
    recommended_path = []
    adaptive_difficulty = DIFFICULTY_LEVELS.get(predicted_mastery, "STANDARD")
    recommended_action = ""
    rationale = ""
    
    if predicted_mastery == "Beginner" or recent_accuracy < 0.65:
        recommended_action = "FOUNDATION_REVISION"
        rationale = (
            f"Model detected lower retention in '{weakest_topic}' ({weakest_score*100:.0f}% accuracy). "
            f"Recommending structured review with immediate feedback to solidify core vocabulary before progressing."
        )
        recommended_path = [
            {"step": 1, "type": "Review", "title": f"Review Core Basics: {weakest_topic}", "duration_min": 3},
            {"step": 2, "type": "Practice", "title": "Vocabulary Flashcards & Audio Practice", "duration_min": 5},
            {"step": 3, "type": "Quiz", "title": "Confidence Check (Untimed)", "duration_min": 4}
        ]
        next_suggested_lesson = f"{weakest_topic} - Essential Review"
        difficulty_adjustment = "Reduced by 25% (Emphasis on retention)"
        
    elif predicted_mastery == "Intermediate":
        recommended_action = "TARGETED_PRACTICE"
        rationale = (
            f"Solid foundational competence demonstrated ({recent_accuracy*100:.0f}% recent accuracy). "
            f"Recommended to focus on bridging the gap in '{weakest_topic}' while maintaining momentum in '{strongest_topic}'."
        )
        recommended_path = [
            {"step": 1, "type": "Practice", "title": f"Targeted Drill: {weakest_topic}", "duration_min": 5},
            {"step": 2, "type": "Challenge", "title": f"Mixed Sentence Structure: {current_topic}", "duration_min": 6},
            {"step": 3, "type": "Milestone", "title": "Unit Progress Assessment", "duration_min": 5}
        ]
        next_suggested_lesson = f"{current_topic} - Mixed Application"
        difficulty_adjustment = "Standard Dynamic Balancing"
        
    else:  # "Advanced"
        recommended_action = "ACCELERATED_CHALLENGE"
        rationale = (
            f"High predicted mastery ({confidence*100:.0f}% confidence) with fast cognitive retrieval "
            f"({avg_response_time:.1f}s latency). Unlocking accelerated rapid-fire syntax modules and advanced conversation units."
        )
        recommended_path = [
            {"step": 1, "type": "Mastery", "title": f"Speed Challenge: {strongest_topic}", "duration_min": 4},
            {"step": 2, "type": "Advanced", "title": "Idiomatic Expressions & Fluent Dialogue", "duration_min": 7},
            {"step": 3, "type": "Honor", "title": "Legendary Mastery Trial", "duration_min": 6}
        ]
        next_suggested_lesson = f"{current_topic} - Legendary Challenge"
        difficulty_adjustment = "Increased by 30% (Speed & Syntax depth)"
        
    return {
        "predicted_mastery": predicted_mastery,
        "recommended_action": recommended_action,
        "recommended_difficulty": adaptive_difficulty,
        "difficulty_adjustment": difficulty_adjustment,
        "next_suggested_lesson": next_suggested_lesson,
        "rationale": rationale,
        "strongest_topic": {"topic": strongest_topic, "accuracy": strongest_score},
        "weakest_topic": {"topic": weakest_topic, "accuracy": weakest_score},
        "personalized_path": recommended_path
    }

