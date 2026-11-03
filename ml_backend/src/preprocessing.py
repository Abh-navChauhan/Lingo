"""
DATA PREPROCESSING AND PIPELINE MODULE
--------------------------------------
Statistical Machine Learning (SML) College Project - Duolingo Adaptive Learning Platform

This module handles:
1. Feature extraction and missing value handling
2. Strict train-test splitting to prevent data leakage
3. One-hot encoding for categorical variables (topic, previous_mastery)
4. Standard scaling for continuous numeric features
5. Export of serialised preprocessing artefacts via joblib
"""

import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
import joblib

NUMERIC_FEATURES = [
    "previous_accuracy",
    "topic_wise_accuracy",
    "number_of_attempts",
    "avg_response_time",
    "completion_rate",
    "learning_consistency",
    "recent_improvement"
]

CATEGORICAL_FEATURES = [
    "topic",
    "previous_mastery"
]

TARGET_COLUMN = "mastery_level"
CLASSES = ["Beginner", "Intermediate", "Advanced"]

def build_preprocessor() -> ColumnTransformer:
    """
    Constructs an sklearn ColumnTransformer ensuring clean encapsulation
    of numeric imputation/scaling and categorical imputation/encoding.
    """
    numeric_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])
    
    categorical_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, NUMERIC_FEATURES),
            ("cat", categorical_transformer, CATEGORICAL_FEATURES)
        ]
    )
    return preprocessor

def prepare_data(data_path: str = None, test_size: float = 0.2, random_state: int = 42):
    """
    Loads dataset, splits into stratified train/test sets to guarantee
    equal class representation across splits, and fits the preprocessor.
    """
    if data_path is None:
        data_path = os.path.join(os.path.dirname(__file__), "..", "data", "student_performance.csv")
        
    df = pd.read_csv(data_path)
    
    # Feature matrix X and label vector y
    X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y = df[TARGET_COLUMN]
    
    # Stratified train-test split prevents target distribution skew and data leakage
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    
    preprocessor = build_preprocessor()
    X_train_processed = preprocessor.fit_transform(X_train)
    X_test_processed = preprocessor.transform(X_test)
    
    # Extract transformed feature names for explainability
    cat_encoder = preprocessor.named_transformers_["cat"].named_steps["onehot"]
    cat_features_out = cat_encoder.get_feature_names_out(CATEGORICAL_FEATURES).tolist()
    all_feature_names = NUMERIC_FEATURES + cat_features_out
    
    return {
        "preprocessor": preprocessor,
        "X_train": X_train,
        "X_test": X_test,
        "X_train_processed": X_train_processed,
        "X_test_processed": X_test_processed,
        "y_train": y_train,
        "y_test": y_test,
        "feature_names": all_feature_names,
        "classes": CLASSES
    }

def save_preprocessor(preprocessor, out_path: str = None):
    if out_path is None:
        out_path = os.path.join(os.path.dirname(__file__), "..", "models", "preprocessor.joblib")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    joblib.dump(preprocessor, out_path)
    print(f"Preprocessing pipeline serialised to: {out_path}")

if __name__ == "__main__":
    data_dict = prepare_data()
    save_preprocessor(data_dict["preprocessor"])
    print(f"X_train shape: {data_dict['X_train_processed'].shape}")
    print(f"X_test shape:  {data_dict['X_test_processed'].shape}")
    print(f"Features: {data_dict['feature_names']}")

