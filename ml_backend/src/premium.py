"""
'EARN YOUR PREMIUM' MERIT-BASED ACCESS CONTROLLER
-------------------------------------------------
Statistical Machine Learning (SML) College Project - Duolingo Adaptive Learning Platform

Replaces traditional commercial payment gateways with a merit-based accessibility
policy. Students unlock temporary premium features purely through active learning
mastery, consistency, and sustained improvement predicted by the ML engine.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List

def evaluate_premium_eligibility(
    predicted_mastery: str,
    confidence: float,
    learning_consistency: float,
    recent_improvement: float,
    recent_accuracy: float,
    number_of_attempts: int
) -> Dict[str, Any]:
    """
    Evaluates whether a student has qualified to unlock premium access based
    on educational performance indicators, generating explainable criteria.
    """
    criteria: List[Dict[str, Any]] = []
    
    # Criterion 1: Mastery Level
    mastery_ok = predicted_mastery in ["Advanced", "Intermediate"]
    criteria.append({
        "name": "ML Mastery Prediction",
        "description": "Predicted at Intermediate or Advanced level",
        "value": f"{predicted_mastery} ({confidence*100:.0f}% confidence)",
        "passed": mastery_ok
    })
    
    # Criterion 2: Learning Consistency
    consistency_ok = learning_consistency >= 0.65
    criteria.append({
        "name": "Learning Consistency Index",
        "description": "Consistent session participation >= 65%",
        "value": f"{learning_consistency*100:.0f}%",
        "passed": consistency_ok
    })
    
    # Criterion 3: Accuracy Threshold
    accuracy_ok = recent_accuracy >= 0.70
    criteria.append({
        "name": "Recent Quiz Accuracy",
        "description": "Accuracy threshold >= 70%",
        "value": f"{recent_accuracy*100:.0f}%",
        "passed": accuracy_ok
    })
    
    # Criterion 4: Improvement or High-Performance Maintenance
    improvement_ok = (recent_improvement >= 0.0) or (recent_accuracy >= 0.85)
    criteria.append({
        "name": "Performance Trajectory",
        "description": "Positive learning trend or sustained elite accuracy",
        "value": f"{'+' if recent_improvement >= 0 else ''}{recent_improvement*100:.1f}% trend",
        "passed": improvement_ok
    })
    
    passed_count = sum(1 for c in criteria if c["passed"])
    progress_percentage = int((passed_count / len(criteria)) * 100)
    
    is_eligible = False
    duration_days = 0
    tier_name = "FREE_TIER"
    benefits = []
    explanation = ""
    
    now = datetime.utcnow()
    
    if predicted_mastery == "Advanced" and passed_count >= 3:
        is_eligible = True
        duration_days = 7
        tier_name = "7_DAY_LEGENDARY_PASS"
        benefits = [
            "Unlimited Hearts (Zero penalties on mistakes)",
            "Personalised AI Review Drills",
            "Legendary Speed Quests & Bonus Gems",
            "Advanced Cultural Insights Modules"
        ]
        explanation = (
            f"Unlocked 7-Day Legendary Pass! Your demonstrated '{predicted_mastery}' mastery, "
            f"{learning_consistency*100:.0f}% consistency, and high accuracy qualified you for full premium access."
        )
    elif predicted_mastery == "Intermediate" and passed_count >= 3:
        is_eligible = True
        duration_days = 3
        tier_name = "3_DAY_PRACTICE_BOOST"
        benefits = [
            "Unlimited Hearts for 3 Days",
            "Targeted Weak-Topic Drills",
            "Progress Recovery Sessions"
        ]
        explanation = (
            f"Unlocked 3-Day Practice Boost! Strong performance across {passed_count} learning benchmarks "
            f"unlocked unlimited hearts and targeted weak-topic drills."
        )
    else:
        is_eligible = False
        duration_days = 0
        tier_name = "FOUNDATION_FREE"
        benefits = ["Standard Core Lessons", "5 Standard Hearts", "Daily Community Quests"]
        explanation = (
            f"Progress: {progress_percentage}% towards Earn-Your-Premium. "
            f"Complete more daily lessons and achieve >= 70% accuracy to unlock free premium benefits!"
        )
        
    unlock_date = now.isoformat() if is_eligible else None
    expiry_date = (now + timedelta(days=duration_days)).isoformat() if is_eligible else None
    
    return {
        "is_eligible": is_eligible,
        "tier": tier_name,
        "duration_days": duration_days,
        "progress_percentage": progress_percentage,
        "unlocked_at": unlock_date,
        "expires_at": expiry_date,
        "benefits": benefits,
        "explanation": explanation,
        "criteria": criteria
    }

