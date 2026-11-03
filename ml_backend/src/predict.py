"""
INFERENCE & PERFORMANCE PREDICTION ENGINE
-----------------------------------------
Statistical Machine Learning (SML) College Project

Loads the serialized preprocessing pipeline and trained statistical models
to generate real-time mastery classifications, class probability distributions,
and student behavioral cluster assignments.
"""

import os
import sys
import pickle

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

import sml_models

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
BEST_MODEL_PATH = os.path.join(MODELS_DIR, "best_model.pkl")
PREPROCESSOR_PATH = os.path.join(MODELS_DIR, "preprocessor.pkl")
KMEANS_PATH = os.path.join(MODELS_DIR, "kmeans_model.pkl")

# Cached model instances in memory
_best_model = None
_preprocessor = None
_kmeans_model = None

def get_models():
    global _best_model, _preprocessor, _kmeans_model
    if _best_model is None:
        with open(BEST_MODEL_PATH, "rb") as f:
            _best_model = pickle.load(f)
        with open(PREPROCESSOR_PATH, "rb") as f:
            _preprocessor = pickle.load(f)
        with open(KMEANS_PATH, "rb") as f:
            _kmeans_model = pickle.load(f)
    return _best_model, _preprocessor, _kmeans_model

def predict_student_mastery(performance_record: dict) -> dict:
    """
    Accepts structured historical student session telemetry and returns:
    - predicted_mastery: "Beginner" | "Intermediate" | "Advanced"
    - confidence: float (0.0 to 1.0)
    - probabilities: dict of class probabilities
    - cluster_id: int (0, 1, 2)
    - cluster_name: str
    """
    model, preprocessor, kmeans = get_models()

    # Format record for preprocessor
    row = {
        "previous_accuracy": float(performance_record.get("previous_accuracy", 0.70)),
        "topic_accuracy": float(performance_record.get("topic_accuracy", 0.70)),
        "num_attempts": int(performance_record.get("num_attempts", 1)),
        "avg_response_time": float(performance_record.get("avg_response_time", 15.0)),
        "completion_rate": float(performance_record.get("completion_rate", 1.0)),
        "learning_consistency": float(performance_record.get("learning_consistency", 0.75)),
        "recent_improvement": float(performance_record.get("recent_improvement", 0.05)),
        "topic": str(performance_record.get("topic", "Spanish Basics")),
        "previous_mastery": str(performance_record.get("previous_mastery", "Intermediate"))
    }

    # Transform features
    X_transformed = preprocessor.transform([row])

    # Supervised Mastery Prediction
    probas = model.predict_proba(X_transformed)[0]
    classes = model.classes
    prob_dict = {cls_name: round(float(prob), 4) for cls_name, prob in zip(classes, probas)}

    # Highest probability class
    best_idx = probas.index(max(probas))
    predicted_mastery = classes[best_idx]
    confidence = round(float(probas[best_idx]), 4)

    # K-Means Cluster Assignment (Behavioral grouping)
    # Uses numerical features: [0..6]
    X_cluster = [[X_transformed[0][i] for i in range(7)]]
    cluster_id = int(kmeans.predict(X_cluster)[0])
    cluster_name = kmeans.cluster_names_.get(cluster_id, "Standard Learner")

    return {
        "predicted_mastery": predicted_mastery,
        "confidence": confidence,
        "probabilities": prob_dict,
        "cluster_id": cluster_id,
        "cluster_name": cluster_name
    }

if __name__ == "__main__":
    test_sample = {
        "previous_accuracy": 0.88,
        "topic_accuracy": 0.92,
        "num_attempts": 1,
        "avg_response_time": 9.2,
        "completion_rate": 1.0,
        "learning_consistency": 0.85,
        "recent_improvement": 0.08,
        "topic": "Spanish Basics",
        "previous_mastery": "Intermediate"
    }
    result = predict_student_mastery(test_sample)
    print("Test Prediction Output:", result)
