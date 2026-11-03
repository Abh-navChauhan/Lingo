"""
STATISTICAL MACHINE LEARNING (SML) CORE ALGORITHMS IMPLEMENTED FROM SCRATCH
----------------------------------------------------------------------------
Subject: Statistical Machine Learning (SML) College Project
Duolingo Adaptive Learning Platform

This module implements the mathematical formulations of:
1. Multinomial Logistic Regression (Softmax + Cross Entropy + L2 Regularization)
2. Decision Tree Classifier (Recursive Binary Splitting + Gini Impurity)
3. Random Forest Classifier (Bootstrap Aggregating + Random Subspace + Majority Voting)
4. K-Means Clustering (Lloyd's Algorithm + Euclidean Distance + Silhouette Scoring)
5. Statistical Data Preprocessing (Z-score StandardScaler + OneHotEncoder)
6. Model Evaluation (Confusion Matrix, Precision, Recall, Macro/Weighted F1, Silhouette)
"""

import math
import random
import json
import os

# ==============================================================================
# 1. STATISTICAL PREPROCESSING (PREVENTS DATA LEAKAGE)
# ==============================================================================

class SMLStandardScaler:
    """Standardize features by removing the mean and scaling to unit variance (Z-score)."""
    def __init__(self):
        self.means = []
        self.stds = []

    def fit(self, X):
        n_samples = len(X)
        n_features = len(X[0])
        self.means = [0.0] * n_features
        self.stds = [1.0] * n_features

        for j in range(n_features):
            col_vals = [X[i][j] for i in range(n_samples)]
            m = sum(col_vals) / n_samples
            var = sum((v - m) ** 2 for v in col_vals) / max(1, n_samples - 1)
            std = math.sqrt(var) if var > 1e-9 else 1.0
            self.means[j] = m
            self.stds[j] = std
        return self

    def transform(self, X):
        X_scaled = []
        for row in X:
            scaled_row = [(row[j] - self.means[j]) / self.stds[j] for j in range(len(row))]
            X_scaled.append(scaled_row)
        return X_scaled

    def fit_transform(self, X):
        return self.fit(X).transform(X)


class SMLOneHotEncoder:
    """Encode categorical features as one-hot numeric arrays."""
    def __init__(self):
        self.categories = {}

    def fit(self, cat_data):
        # cat_data: list of dicts or list of string lists
        n_features = len(cat_data[0])
        self.categories = {j: sorted(list(set(row[j] for row in cat_data))) for j in range(n_features)}
        return self

    def transform(self, cat_data):
        encoded = []
        for row in cat_data:
            enc_row = []
            for j, val in enumerate(row):
                cats = self.categories.get(j, [])
                for c in cats:
                    enc_row.append(1.0 if val == c else 0.0)
            encoded.append(enc_row)
        return encoded


class SMLPipeline:
    """Combines categorical one-hot encoding and numerical standardization."""
    def __init__(self, num_cols, cat_cols):
        self.num_cols = num_cols
        self.cat_cols = cat_cols
        self.scaler = SMLStandardScaler()
        self.encoder = SMLOneHotEncoder()
        self.feature_names = []

    def fit(self, rows):
        num_data = [[float(r[col]) for col in self.num_cols] for r in rows]
        cat_data = [[str(r[col]) for col in self.cat_cols] for r in rows]

        self.scaler.fit(num_data)
        self.encoder.fit(cat_data)

        # Build feature names
        self.feature_names = list(self.num_cols)
        for j, col_name in enumerate(self.cat_cols):
            for c in self.encoder.categories[j]:
                self.feature_names.append(f"{col_name}_{c}")
        return self

    def transform(self, rows):
        num_data = [[float(r[col]) for col in self.num_cols] for r in rows]
        cat_data = [[str(r[col]) for col in self.cat_cols] for r in rows]

        scaled_num = self.scaler.transform(num_data)
        encoded_cat = self.encoder.transform(cat_data)

        combined = []
        for i in range(len(rows)):
            combined.append(scaled_num[i] + encoded_cat[i])
        return combined

    def fit_transform(self, rows):
        return self.fit(rows).transform(rows)


# ==============================================================================
# 2. LOGISTIC REGRESSION (MULTINOMIAL SOFTMAX REGRESSION)
# ==============================================================================

class SMLLogisticRegression:
    """
    Multinomial Logistic Regression using Softmax and Gradient Descent with L2 Regularization.
    Mathematical formulation:
        P(Y = k | X) = exp(w_k^T X) / sum_j exp(w_j^T X)
        Loss J(W) = -1/N sum_i log(P(Y = y_i | X_i)) + (lambda / 2) * ||W||^2
    """
    def __init__(self, lr=0.08, n_iters=400, l2_reg=0.001):
        self.lr = lr
        self.n_iters = n_iters
        self.l2_reg = l2_reg
        self.classes = []
        self.weights = [] # Shape: (n_classes, n_features + 1 for bias)

    def _softmax(self, z):
        max_z = max(z)
        exp_z = [math.exp(val - max_z) for val in z]
        sum_exp = sum(exp_z)
        return [val / max_exp if (max_exp := max(sum_exp, 1e-12)) else 1.0 / len(z) for val in exp_z]

    def fit(self, X, y):
        self.classes = sorted(list(set(y)))
        n_samples = len(X)
        n_features = len(X[0])
        n_classes = len(self.classes)

        class_to_idx = {c: i for i, c in enumerate(self.classes)}
        # Initialize weights with small random Gaussian values
        random.seed(42)
        self.weights = [[(random.random() - 0.5) * 0.05 for _ in range(n_features + 1)] for _ in range(n_classes)]

        for it in range(self.n_iters):
            # Compute gradients
            grad = [[0.0] * (n_features + 1) for _ in range(n_classes)]

            for i in range(n_samples):
                xi = [1.0] + X[i] # prepend bias term 1.0
                yi = class_to_idx[y[i]]

                # Logits z_k = W_k . x
                logits = [sum(self.weights[c][f] * xi[f] for f in range(n_features + 1)) for c in range(n_classes)]
                probs = self._softmax(logits)

                for c in range(n_classes):
                    target = 1.0 if c == yi else 0.0
                    err = probs[c] - target
                    for f in range(n_features + 1):
                        grad[c][f] += err * xi[f]

            # Update weights with L2 penalty on non-bias coefficients
            for c in range(n_classes):
                for f in range(n_features + 1):
                    reg = self.l2_reg * self.weights[c][f] if f > 0 else 0.0
                    self.weights[c][f] -= self.lr * (grad[c][f] / n_samples + reg)

        return self

    def predict_proba(self, X):
        probas = []
        n_classes = len(self.classes)
        for row in X:
            xi = [1.0] + row
            logits = [sum(self.weights[c][f] * xi[f] for f in range(len(xi))) for c in range(n_classes)]
            probas.append(self._softmax(logits))
        return probas

    def predict(self, X):
        probas = self.predict_proba(X)
        return [self.classes[p.index(max(p))] for p in probas]


# ==============================================================================
# 3. DECISION TREE CLASSIFIER (RECURSIVE BINARY SPLITTING VIA GINI IMPURITY)
# ==============================================================================

class SMLDecisionNode:
    def __init__(self, feature=None, threshold=None, left=None, right=None, probs=None, value=None):
        self.feature = feature
        self.threshold = threshold
        self.left = left
        self.right = right
        self.probs = probs
        self.value = value

    @property
    def is_leaf(self):
        return self.value is not None


class SMLDecisionTreeClassifier:
    """
    Classification Tree using Gini Impurity reduction:
        Gini(S) = 1 - sum_{c} p_c^2
        Information Gain = Gini(parent) - (N_left/N * Gini_left + N_right/N * Gini_right)
    """
    def __init__(self, max_depth=5, min_samples_split=6):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.root = None
        self.classes = []
        self.feature_importances_ = []

    def _gini(self, y_sub):
        n = len(y_sub)
        if n == 0:
            return 0.0
        counts = {}
        for label in y_sub:
            counts[label] = counts.get(label, 0) + 1
        return 1.0 - sum((count / n) ** 2 for count in counts.values())

    def _best_split(self, X, y, feat_indices):
        best_gain = -1.0
        best_feat = None
        best_thresh = None
        current_gini = self._gini(y)
        n = len(y)

        for feat in feat_indices:
            vals = [X[i][feat] for i in range(n)]
            unique_vals = sorted(list(set(vals)))
            if len(unique_vals) <= 1:
                continue

            # Candidate thresholds as midpoints
            step = max(1, len(unique_vals) // 8)
            thresholds = [(unique_vals[k] + unique_vals[k + 1]) / 2.0 for k in range(0, len(unique_vals) - 1, step)]

            for thresh in thresholds:
                left_y = [y[i] for i in range(n) if X[i][feat] <= thresh]
                right_y = [y[i] for i in range(n) if X[i][feat] > thresh]

                if not left_y or not right_y:
                    continue

                gain = current_gini - (len(left_y)/n * self._gini(left_y) + len(right_y)/n * self._gini(right_y))
                if gain > best_gain:
                    best_gain = gain
                    best_feat = feat
                    best_thresh = thresh

        return best_feat, best_thresh, best_gain

    def _build_tree(self, X, y, depth=0, feat_indices=None):
        n_samples = len(y)
        counts = {c: 0 for c in self.classes}
        for label in y:
            counts[label] += 1
        probs = [counts[c] / n_samples for c in self.classes]
        majority_val = max(counts, key=counts.get)

        # Stopping criteria
        if (depth >= self.max_depth or 
            n_samples < self.min_samples_split or 
            len(set(y)) == 1):
            return SMLDecisionNode(probs=probs, value=majority_val)

        feat_idx = feat_indices if feat_indices is not None else list(range(len(X[0])))
        best_feat, best_thresh, best_gain = self._best_split(X, y, feat_idx)

        if best_feat is None or best_gain <= 1e-6:
            return SMLDecisionNode(probs=probs, value=majority_val)

        # Accumulate feature importance
        self.feature_importances_[best_feat] += best_gain * n_samples

        left_idx = [i for i in range(n_samples) if X[i][best_feat] <= best_thresh]
        right_idx = [i for i in range(n_samples) if X[i][best_feat] > best_thresh]

        left_child = self._build_tree([X[i] for i in left_idx], [y[i] for i in left_idx], depth + 1, feat_indices)
        right_child = self._build_tree([X[i] for i in right_idx], [y[i] for i in right_idx], depth + 1, feat_indices)

        return SMLDecisionNode(feature=best_feat, threshold=best_thresh, left=left_child, right=right_child, probs=probs)

    def fit(self, X, y):
        self.classes = sorted(list(set(y)))
        self.feature_importances_ = [0.0] * len(X[0])
        self.root = self._build_tree(X, y)

        # Normalize feature importances
        tot = sum(self.feature_importances_)
        if tot > 0:
            self.feature_importances_ = [fi / tot for fi in self.feature_importances_]
        return self

    def _predict_row(self, node, row):
        if node.is_leaf:
            return node.probs
        if row[node.feature] <= node.threshold:
            return self._predict_row(node.left, row)
        return self._predict_row(node.right, row)

    def predict_proba(self, X):
        return [self._predict_row(self.root, row) for row in X]

    def predict(self, X):
        probas = self.predict_proba(X)
        return [self.classes[p.index(max(p))] for p in probas]


# ==============================================================================
# 4. RANDOM FOREST CLASSIFIER (BAGGING ENSEMBLE OF DECISION TREES)
# ==============================================================================

class SMLRandomForestClassifier:
    """
    Random Forest ensemble combining:
    1. Bootstrap aggregating (sampling with replacement)
    2. Random feature subspace selection (sqrt(num_features))
    3. Soft-voting probability averaging across trees
    """
    def __init__(self, n_estimators=15, max_depth=6, min_samples_split=5, random_state=42):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.random_state = random_state
        self.trees = []
        self.classes = []
        self.feature_importances_ = []

    def fit(self, X, y):
        random.seed(self.random_state)
        self.classes = sorted(list(set(y)))
        n_samples = len(X)
        n_features = len(X[0])
        self.trees = []
        self.feature_importances_ = [0.0] * n_features

        subspace_size = max(1, int(math.sqrt(n_features)))

        for i in range(self.n_estimators):
            # 1. Bootstrap sample (with replacement)
            boot_idx = [random.randint(0, n_samples - 1) for _ in range(n_samples)]
            X_boot = [X[idx] for idx in boot_idx]
            y_boot = [y[idx] for idx in boot_idx]

            # 2. Random feature subspace
            feat_subset = random.sample(range(n_features), subspace_size)

            # 3. Train base tree
            tree = SMLDecisionTreeClassifier(max_depth=self.max_depth, min_samples_split=self.min_samples_split)
            tree.classes = self.classes
            tree.feature_importances_ = [0.0] * n_features
            tree.root = tree._build_tree(X_boot, y_boot, depth=0, feat_indices=feat_subset)
            self.trees.append(tree)

            for f in range(n_features):
                self.feature_importances_[f] += tree.feature_importances_[f]

        # Normalize ensemble feature importance
        tot = sum(self.feature_importances_)
        if tot > 0:
            self.feature_importances_ = [round(fi / tot, 4) for fi in self.feature_importances_]
        return self

    def predict_proba(self, X):
        n_classes = len(self.classes)
        avg_probs = []
        for row in X:
            tree_probs = [tree._predict_row(tree.root, row) for tree in self.trees]
            prob_sum = [0.0] * n_classes
            for p in tree_probs:
                for c in range(n_classes):
                    prob_sum[c] += p[c]
            avg_probs.append([round(ps / self.n_estimators, 4) for ps in prob_sum])
        return avg_probs

    def predict(self, X):
        probas = self.predict_proba(X)
        return [self.classes[p.index(max(p))] for p in probas]


# ==============================================================================
# 5. K-MEANS CLUSTERING (LLOYD'S ALGORITHM & SILHOUETTE ANALYSIS)
# ==============================================================================

class SMLKMeans:
    """
    K-Means clustering algorithm using Euclidean distance and centroid recalculation.
    Minimizes within-cluster sum of squares (WCSS / Inertia):
        J = sum_{k=1}^K sum_{x in S_k} ||x - mu_k||^2
    """
    def __init__(self, k=3, max_iter=100, random_state=42):
        self.k = k
        self.max_iter = max_iter
        self.random_state = random_state
        self.centroids = []
        self.inertia_ = 0.0
        self.cluster_names_ = {
            0: "Rapid Fluent Achievers",
            1: "Steady Methodical Learners",
            2: "Struggling Foundation Needers"
        }

    def _dist_sq(self, a, b):
        return sum((a[i] - b[i]) ** 2 for i in range(len(a)))

    def fit(self, X):
        random.seed(self.random_state)
        n_samples = len(X)
        n_features = len(X[0])

        # K-Means++ initialization
        self.centroids = [X[random.randint(0, n_samples - 1)]]
        while len(self.centroids) < self.k:
            distances = [min(self._dist_sq(row, c) for c in self.centroids) for row in X]
            total_dist = sum(distances)
            r = random.uniform(0, max(total_dist, 1e-6))
            cum = 0.0
            chosen = X[-1]
            for row, d in zip(X, distances):
                cum += d
                if cum >= r:
                    chosen = row
                    break
            self.centroids.append(chosen)

        for _ in range(self.max_iter):
            # Assignment step
            clusters = [[] for _ in range(self.k)]
            for row in X:
                nearest = min(range(self.k), key=lambda c: self._dist_sq(row, self.centroids[c]))
                clusters[nearest].append(row)

            # Update step
            new_centroids = []
            for c in range(self.k):
                if not clusters[c]:
                    new_centroids.append(self.centroids[c])
                else:
                    new_mean = [sum(row[f] for row in clusters[c]) / len(clusters[c]) for f in range(n_features)]
                    new_centroids.append(new_mean)

            # Check convergence
            shift = sum(self._dist_sq(self.centroids[c], new_centroids[c]) for c in range(self.k))
            self.centroids = new_centroids
            if shift < 1e-6:
                break

        # Calculate inertia
        self.inertia_ = sum(min(self._dist_sq(row, c) for c in self.centroids) for row in X)
        return self

    def predict(self, X):
        return [min(range(self.k), key=lambda c: self._dist_sq(row, self.centroids[c])) for row in X]

    def silhouette_score(self, X, labels):
        """Calculates mean silhouette coefficient for cluster validation."""
        n = len(X)
        if n > 400: # subsample for fast computation
            random.seed(42)
            sub_idx = random.sample(range(n), 400)
            X = [X[i] for i in sub_idx]
            labels = [labels[i] for i in sub_idx]
            n = len(X)

        s_scores = []
        for i in range(n):
            same_cluster = [X[j] for j in range(n) if j != i and labels[j] == labels[i]]
            if not same_cluster:
                s_scores.append(0.0)
                continue
            a_i = sum(math.sqrt(self._dist_sq(X[i], pt)) for pt in same_cluster) / len(same_cluster)

            other_clusters = set(labels) - {labels[i]}
            b_i = float("inf")
            for oc in other_clusters:
                pts = [X[j] for j in range(n) if labels[j] == oc]
                if pts:
                    avg_d = sum(math.sqrt(self._dist_sq(X[i], pt)) for pt in pts) / len(pts)
                    if avg_d < b_i:
                        b_i = avg_d

            s_i = (b_i - a_i) / max(a_i, b_i) if max(a_i, b_i) > 0 else 0.0
            s_scores.append(s_i)

        return round(sum(s_scores) / len(s_scores), 4)


# ==============================================================================
# 6. SML EVALUATION METRICS
# ==============================================================================

def accuracy_score(y_true, y_pred):
    correct = sum(1 for yt, yp in zip(y_true, y_pred) if yt == yp)
    return round(correct / len(y_true), 4)

def confusion_matrix(y_true, y_pred, labels):
    idx_map = {l: i for i, l in enumerate(labels)}
    k = len(labels)
    cm = [[0] * k for _ in range(k)]
    for yt, yp in zip(y_true, y_pred):
        if yt in idx_map and yp in idx_map:
            cm[idx_map[yt]][idx_map[yp]] += 1
    return cm

def classification_report(y_true, y_pred, labels):
    cm = confusion_matrix(y_true, y_pred, labels)
    k = len(labels)
    report = {}

    tot_support = len(y_true)
    weighted_p, weighted_r, weighted_f1 = 0.0, 0.0, 0.0
    macro_p, macro_r, macro_f1 = 0.0, 0.0, 0.0

    for i, lbl in enumerate(labels):
        tp = cm[i][i]
        fp = sum(cm[row][i] for row in range(k) if row != i)
        fn = sum(cm[i][col] for col in range(k) if col != i)
        supp = sum(cm[i])

        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0

        report[lbl] = {
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1-score": round(f1, 4),
            "support": supp
        }

        macro_p += prec
        macro_r += rec
        macro_f1 += f1

        weighted_p += prec * supp
        weighted_r += rec * supp
        weighted_f1 += f1 * supp

    report["accuracy"] = accuracy_score(y_true, y_pred)
    report["macro avg"] = {
        "precision": round(macro_p / k, 4),
        "recall": round(macro_r / k, 4),
        "f1-score": round(macro_f1 / k, 4),
        "support": tot_support
    }
    report["weighted avg"] = {
        "precision": round(weighted_p / tot_support, 4),
        "recall": round(weighted_r / tot_support, 4),
        "f1-score": round(weighted_f1 / tot_support, 4),
        "support": tot_support
    }
    return report


# ==============================================================================
# 7. VECTOR VISUALIZATIONS GENERATOR (SVG - ZERO HEAVY LIBS REQUIRED)
# ==============================================================================

def generate_confusion_matrix_svg(cm, labels, title="Confusion Matrix"):
    n = len(labels)
    cell_size = 80
    pad = 100
    w = pad * 2 + n * cell_size
    h = pad * 2 + n * cell_size
    max_val = max(max(row) for row in cm) or 1

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" style="background:#0f172a; font-family:sans-serif;">']
    svg.append(f'<text x="{w/2}" y="40" text-anchor="middle" fill="#f8fafc" font-size="18" font-weight="bold">{title}</text>')
    svg.append(f'<text x="{w/2}" y="65" text-anchor="middle" fill="#94a3b8" font-size="12">Predicted Class &rarr;</text>')

    for i in range(n):
        # Y label (True)
        svg.append(f'<text x="{pad - 15}" y="{pad + i*cell_size + cell_size/2 + 5}" text-anchor="end" fill="#cbd5e1" font-size="13" font-weight="600">{labels[i]}</text>')
        # X label (Pred)
        svg.append(f'<text x="{pad + i*cell_size + cell_size/2}" y="{pad - 10}" text-anchor="middle" fill="#cbd5e1" font-size="13" font-weight="600">{labels[i]}</text>')

        for j in range(n):
            val = cm[i][j]
            alpha = max(0.12, val / max_val)
            color = f"rgba(59, 130, 246, {alpha:.3f})" if i == j else f"rgba(239, 68, 68, {alpha*0.8:.3f})"
            x = pad + j * cell_size
            y = pad + i * cell_size

            svg.append(f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" fill="{color}" stroke="#334155" stroke-width="1.5" rx="4"/>')
            svg.append(f'<text x="{x + cell_size/2}" y="{y + cell_size/2 + 6}" text-anchor="middle" fill="#ffffff" font-size="16" font-weight="bold">{val}</text>')

    svg.append(f'<text x="25" y="{h/2}" transform="rotate(-90 25 {h/2})" text-anchor="middle" fill="#94a3b8" font-size="12">True Class</text>')
    svg.append('</svg>')
    return "\n".join(svg)

def generate_model_comparison_svg(comparison_data):
    w, h = 750, 400
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" style="background:#0f172a; font-family:sans-serif;">']
    svg.append(f'<text x="{w/2}" y="35" text-anchor="middle" fill="#f8fafc" font-size="20" font-weight="bold">Supervised Algorithm Performance Comparison</text>')
    svg.append(f'<text x="{w/2}" y="60" text-anchor="middle" fill="#94a3b8" font-size="12">Test Set Accuracy, Macro-F1 &amp; Weighted-F1 Metrics</text>')

    models = list(comparison_data.keys())
    metrics = ["accuracy", "macro_f1", "weighted_f1"]
    colors = ["#3b82f6", "#10b981", "#8b5cf6"]

    pad_l, pad_b = 140, 80
    chart_w, chart_h = 560, 240
    group_w = chart_w / len(models)

    # Gridlines
    for v in [0.2, 0.4, 0.6, 0.8, 1.0]:
        y = pad_b + chart_h - (v * chart_h)
        svg.append(f'<line x1="{pad_l}" y1="{y}" x2="{pad_l + chart_w}" y2="{y}" stroke="#334155" stroke-dasharray="3,3" />')
        svg.append(f'<text x="{pad_l - 10}" y="{y + 4}" text-anchor="end" fill="#64748b" font-size="11">{int(v*100)}%</text>')

    bar_w = 26
    for m_idx, m_name in enumerate(models):
        group_x = pad_l + m_idx * group_w + 30
        for b_idx, met in enumerate(metrics):
            val = comparison_data[m_name][met]
            bar_h = val * chart_h
            bx = group_x + b_idx * (bar_w + 4)
            by = pad_b + chart_h - bar_h

            svg.append(f'<rect x="{bx}" y="{by}" width="{bar_w}" height="{bar_h}" fill="{colors[b_idx]}" rx="4" />')
            svg.append(f'<text x="{bx + bar_w/2}" y="{by - 6}" text-anchor="middle" fill="#e2e8f0" font-size="10" font-weight="bold">{val:.1%}</text>')

        svg.append(f'<text x="{group_x + bar_w*1.5}" y="{pad_b + chart_h + 25}" text-anchor="middle" fill="#cbd5e1" font-size="12" font-weight="600">{m_name}</text>')

    # Legend
    legend_labels = ["Accuracy", "Macro F1", "Weighted F1"]
    for l_idx, (col, lbl) in enumerate(zip(colors, legend_labels)):
        lx = pad_l + l_idx * 150 + 60
        ly = h - 20
        svg.append(f'<rect x="{lx}" y="{ly - 10}" width="14" height="14" fill="{col}" rx="3"/>')
        svg.append(f'<text x="{lx + 20}" y="{ly + 2}" fill="#cbd5e1" font-size="12">{lbl}</text>')

    svg.append('</svg>')
    return "\n".join(svg)

