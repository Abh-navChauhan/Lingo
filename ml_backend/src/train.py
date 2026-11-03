"""
MODEL TRAINING, EVALUATION & ALGORITHM COMPARISON PIPELINE
---------------------------------------------------------
Statistical Machine Learning (SML) College Project

Implements rigorous model training, validation, and empirical algorithm comparison:
1. Multinomial Logistic Regression
2. Decision Tree Classifier
3. Random Forest Classifier
4. K-Means Behavioral Clustering

Evaluates:
- Accuracy, Precision, Recall, Macro-F1, Weighted-F1
- Confusion Matrix per model
- K-Means Silhouette Score and Cluster Profiling
- Saves best-performing model for real-time inference
"""

import os
import csv
import json
import pickle
import random
from sml_models import (
    SMLPipeline,
    SMLLogisticRegression,
    SMLDecisionTreeClassifier,
    SMLRandomForestClassifier,
    SMLKMeans,
    accuracy_score,
    confusion_matrix,
    classification_report,
    generate_confusion_matrix_svg,
    generate_model_comparison_svg
)

NUM_COLS = [
    "previous_accuracy",
    "topic_accuracy",
    "num_attempts",
    "avg_response_time",
    "completion_rate",
    "learning_consistency",
    "recent_improvement"
]

CAT_COLS = [
    "topic",
    "previous_mastery"
]

TARGET_COL = "target_mastery"
MASTERY_CLASSES = ["Beginner", "Intermediate", "Advanced"]

def load_data(filepath: str):
    with open(filepath, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

def train_test_split(rows, test_ratio=0.20, seed=42):
    random.seed(seed)
    shuffled = list(rows)
    random.shuffle(shuffled)
    n_test = int(len(shuffled) * test_ratio)
    return shuffled[n_test:], shuffled[:n_test]

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, "data", "student_performance.csv")
    models_dir = os.path.join(base_dir, "models")
    notebooks_dir = os.path.join(base_dir, "notebooks")
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(notebooks_dir, exist_ok=True)

    print("=" * 70)
    print("STATISTICAL MACHINE LEARNING (SML) - MODEL TRAINING & COMPARISON")
    print("=" * 70)

    # 1. Load Dataset
    print(f"\n[1/6] Loading synthetic performance dataset: {data_path}")
    raw_data = load_data(data_path)
    print(f"      Total records: {len(raw_data)}")

    # 2. Train-Test Split (80% train, 20% test to prevent data leakage)
    print("\n[2/6] Splitting dataset (80% Train, 20% Test) with fixed random seed...")
    train_rows, test_rows = train_test_split(raw_data, test_ratio=0.20, seed=42)
    print(f"      Training samples: {len(train_rows)} | Test samples: {len(test_rows)}")

    # 3. Fit Statistical Preprocessing Pipeline
    print("\n[3/6] Fitting Preprocessing Pipeline (Z-Score Standardization + OneHot Encoding)...")
    pipeline = SMLPipeline(num_cols=NUM_COLS, cat_cols=CAT_COLS)
    X_train = pipeline.fit_transform(train_rows)
    y_train = [r[TARGET_COL] for r in train_rows]

    X_test = pipeline.transform(test_rows)
    y_test = [r[TARGET_COL] for r in test_rows]
    print(f"      Transformed feature space dimensionality: {len(X_train[0])} features")

    # 4. Train Supervised Models
    print("\n[4/6] Training Supervised Machine Learning Algorithms...")
    models = {
        "Logistic Regression": SMLLogisticRegression(lr=0.10, n_iters=450, l2_reg=0.002),
        "Decision Tree": SMLDecisionTreeClassifier(max_depth=5, min_samples_split=6),
        "Random Forest": SMLRandomForestClassifier(n_estimators=18, max_depth=6, min_samples_split=5, random_state=42)
    }

    comparison_results = {}
    fitted_models = {}

    for name, model in models.items():
        print(f"      Training {name}...")
        model.fit(X_train, y_train)
        fitted_models[name] = model

        # Evaluate on Test Set
        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, labels=MASTERY_CLASSES)
        cm = confusion_matrix(y_test, y_pred, labels=MASTERY_CLASSES)

        comparison_results[name] = {
            "accuracy": acc,
            "macro_f1": report["macro avg"]["f1-score"],
            "weighted_f1": report["weighted avg"]["f1-score"],
            "macro_precision": report["macro avg"]["precision"],
            "macro_recall": report["macro avg"]["recall"],
            "confusion_matrix": cm,
            "classification_report": report
        }

        print(f"      -> {name}: Test Accuracy = {acc:.2%}, Macro-F1 = {report['macro avg']['f1-score']:.4f}")

    # 5. Train Unsupervised K-Means Clustering
    print("\n[5/6] Training Unsupervised K-Means Clustering (Student Behavioral Segmentation)...")
    # For clustering, use behavioral telemetry features: accuracy, attempts, response time, consistency
    clustering_num_features = [0, 1, 2, 3, 4, 5, 6]
    X_cluster = [[row[idx] for idx in clustering_num_features] for row in X_train]

    kmeans = SMLKMeans(k=3, max_iter=100, random_state=42)
    kmeans.fit(X_cluster)
    cluster_labels = kmeans.predict(X_cluster)
    sil_score = kmeans.silhouette_score(X_cluster, cluster_labels)

    print(f"      K-Means Inertia: {kmeans.inertia_:.2f}")
    print(f"      K-Means Silhouette Score: {sil_score:.4f}")
    for c_id, c_name in kmeans.cluster_names_.items():
        count = sum(1 for l in cluster_labels if l == c_id)
        print(f"      Cluster {c_id} ({c_name}): {count} students ({count/len(cluster_labels):.1%})")

    # 6. Model Selection & Export
    print("\n[6/6] Algorithm Comparison & Model Serialization...")
    # Select best model based on highest Macro-F1 score on test set
    best_model_name = max(comparison_results, key=lambda m: comparison_results[m]["macro_f1"])
    best_model = fitted_models[best_model_name]

    print(f"\n" + "-" * 70)
    print(f"*** BEST PERFORMING MODEL: {best_model_name.upper()} ***")
    print(f"    Test Accuracy : {comparison_results[best_model_name]['accuracy']:.2%}")
    print(f"    Macro F1-Score: {comparison_results[best_model_name]['macro_f1']:.4f}")
    print(f"    Weighted F1   : {comparison_results[best_model_name]['weighted_f1']:.4f}")
    print("-" * 70)

    # Save Models with standard pickle
    best_model_path = os.path.join(models_dir, "best_model.pkl")
    preprocessor_path = os.path.join(models_dir, "preprocessor.pkl")
    kmeans_path = os.path.join(models_dir, "kmeans_model.pkl")

    with open(best_model_path, "wb") as f:
        pickle.dump(best_model, f)
    with open(preprocessor_path, "wb") as f:
        pickle.dump(pipeline, f)
    with open(kmeans_path, "wb") as f:
        pickle.dump(kmeans, f)

    print(f"\n[OK] Serialized best model to: {best_model_path}")
    print(f"[OK] Serialized preprocessor to: {preprocessor_path}")
    print(f"[OK] Serialized K-Means clustering to: {kmeans_path}")

    # Generate Evaluation Artifacts
    report_json_path = os.path.join(notebooks_dir, "model_comparison_report.json")
    full_report = {
        "metadata": {
            "total_samples": len(raw_data),
            "train_samples": len(train_rows),
            "test_samples": len(test_rows),
            "best_algorithm": best_model_name,
            "classes": MASTERY_CLASSES
        },
        "supervised_comparison": comparison_results,
        "kmeans_clustering": {
            "k": 3,
            "inertia": round(kmeans.inertia_, 2),
            "silhouette_score": sil_score,
            "clusters": kmeans.cluster_names_
        }
    }
    with open(report_json_path, "w", encoding="utf-8") as f:
        json.dump(full_report, f, indent=2)

    # Generate SVG Charts
    cm_svg = generate_confusion_matrix_svg(
        comparison_results[best_model_name]["confusion_matrix"],
        MASTERY_CLASSES,
        title=f"Confusion Matrix: {best_model_name} (Test Set)"
    )
    with open(os.path.join(notebooks_dir, "confusion_matrix.svg"), "w", encoding="utf-8") as f:
        f.write(cm_svg)

    comp_svg = generate_model_comparison_svg(comparison_results)
    with open(os.path.join(notebooks_dir, "model_comparison.svg"), "w", encoding="utf-8") as f:
        f.write(comp_svg)

    print(f"[OK] Exported evaluation report: {report_json_path}")
    print(f"[OK] Exported Confusion Matrix SVG: {os.path.join(notebooks_dir, 'confusion_matrix.svg')}")
    print(f"[OK] Exported Algorithm Comparison SVG: {os.path.join(notebooks_dir, 'model_comparison.svg')}")
    print("\nTraining and evaluation pipeline completed successfully!")

if __name__ == "__main__":
    main()
