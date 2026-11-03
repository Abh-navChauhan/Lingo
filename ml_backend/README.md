# Lingo: Statistical Machine Learning (SML) Adaptive Language Platform

**Academic Project:** Statistical Machine Learning (SML)  
**System:** Full-Stack Adaptive Language Learning Application with Real-Time ML Behavioral Analytics & Merit-Based Access Control

---

## 1. System Architecture Overview

```
                                      +---------------------------------------------+
                                      |                STUDENT CLIENT               |
                                      |    Next.js 14 + React + Tailwind + Clerk    |
                                      +---------------------------------------------+
                                                             |
                           1. Complete Quiz Telemetry        | 4. Fetch Predicted Insights
                           (Latency, Attempts, Accuracy)     |    & Earned Premium Status
                                                             v
+------------------------------------+             +--------------------------------+
|          NEON POSTGRESQL           |<----------->|      NEXT.JS SERVER ACTIONS    |
|   - user_learning_sessions         |             |   - recordLearningSession()    |
|   - user_earned_premium            |             |   - claimEarnedPremium()       |
|   - user_progress / challenges     |             |   - getLearningSessionHistory()|
+------------------------------------+             +--------------------------------+
                                                             |
                                      2. Forward Raw Features| 3. Return Model Predictions,
                                         to SML Pipeline     |    Adaptive Recommendation
                                                             v    & Premium Status
                                            +---------------------------------+
                                            |     FASTAPI / PYTHON ML ENGINE  |
                                            |         (Port 8000)             |
                                            |   - Preprocessing Pipeline      |
                                            |   - Logistic Regression Model   |
                                            |   - K-Means Clustering Engine   |
                                            |   - Pedagogical Recommender     |
                                            +---------------------------------+
```

---

## 2. Mathematical Formulations (SML Viva Defense)

### A. Multinomial Logistic Regression (Best Performing Model: 91.94% Test Accuracy)
Used for classifying student readiness into **Beginner**, **Intermediate**, or **Advanced**.

1. **Softmax Hypothesis Function:**
   $$P(Y = k \mid X) = \frac{e^{w_k^T X + b_k}}{\sum_{j=1}^{K} e^{w_j^T X + b_j}}$$

2. **Categorical Cross-Entropy Objective with $L_2$ Regularization:**
   $$J(W) = -\frac{1}{N} \sum_{i=1}^{N} \sum_{k=1}^{K} y_{ik} \ln(\hat{p}_{ik}) + \frac{\lambda}{2} \sum_{k=1}^{K} \|w_k\|_2^2$$

3. **Gradient Descent Update Rule:**
   $$\nabla_{w_k} J = \frac{1}{N} \sum_{i=1}^{N} (\hat{p}_{ik} - y_{ik}) X_i + \lambda w_k$$
   $$W^{(t+1)} = W^{(t)} - \eta \nabla_W J$$

---

### B. Decision Tree Classifier (Test Accuracy: 87.22%)
Constructs recursive binary decision boundaries based on feature impurity reduction.

1. **Gini Impurity Metric:**
   $$\text{Gini}(S) = 1 - \sum_{k=1}^{K} p_k^2$$

2. **Information Gain of Split ($S \to S_L \cup S_R$):**
   $$\Delta \text{Gini}(S, f, \theta) = \text{Gini}(S) - \left( \frac{|S_L|}{|S|} \text{Gini}(S_L) + \frac{|S_R|}{|S|} \text{Gini}(S_R) \right)$$
   The split $(f^*, \theta^*)$ maximizing $\Delta \text{Gini}$ is selected at each non-terminal node until $\text{depth} \ge 5$ or $|S| < 6$.

---

### C. Random Forest Classifier (Test Accuracy: 87.22%)
Ensemble of $B = 18$ decorrelated decision trees using bootstrap aggregation (Bagging) and random feature sub-spacing:
1. Draw $B$ bootstrap samples $\mathcal{D}_b \subset \mathcal{D}$ with replacement ($|\mathcal{D}_b| = N$).
2. At each split, sample $m = \lfloor\sqrt{D}\rfloor$ features uniformly at random.
3. Aggregate predictions via soft-voting probability averaging:
   $$\hat{P}(Y = k \mid X) = \frac{1}{B} \sum_{b=1}^{B} P_b(Y = k \mid X)$$

---

### D. K-Means Clustering (Unsupervised Behavioral Segmentation)
Identifies latent student archetypes by iteratively minimizing Within-Cluster Sum of Squares (Inertia):

$$J = \sum_{k=1}^{K} \sum_{x \in \mathcal{C}_k} \|x - \mu_k\|_2^2$$

**Student Behavioral Archetypes Discovered:**
- **Cluster 0: Rapid Fluent Achievers (29.3%)** — High accuracy, response latency $< 10\text{s}$, low attempts.
- **Cluster 1: Steady Methodical Learners (44.6%)** — Moderate accuracy, steady response pacing ($15\text{--}20\text{s}$), consistent practice.
- **Cluster 2: Struggling Foundation Needers (26.1%)** — Low retention, multi-attempt retries, high response latency ($>24\text{s}$).

**Silhouette Coefficient Validation:**
$$s(i) = \frac{b(i) - a(i)}{\max(a(i), b(i))}, \quad \text{Mean Silhouette Score} = 0.2179$$

---

### E. Data Preprocessing & Data Leakage Prevention
To prevent data leakage, all statistical parameters ($\mu$, $\sigma$, category vocabularies) are calculated strictly on the **Training Set (80%)** and then applied to the **Test Set (20%)**:
- **Z-Score Normalization:** $Z = \frac{X - \mu_{\text{train}}}{\sigma_{\text{train}}}$
- **One-Hot Categorical Encoding:** Maps nominal variables (`topic`, `previous_mastery`) into binary coordinate vectors.

---

## 3. Empirical Model Comparison Summary

| Algorithm | Test Accuracy | Macro Precision | Macro Recall | Macro F1-Score | Weighted F1 | Selection |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Multinomial Logistic Regression** | **91.94%** | **0.9208** | **0.9184** | **0.9193** | **0.9193** | **Selected Best** |
| Decision Tree Classifier | 87.22% | 0.8711 | 0.8701 | 0.8705 | 0.8705 | Evaluated |
| Random Forest Classifier | 87.22% | 0.8735 | 0.8715 | 0.8724 | 0.8724 | Evaluated |
| K-Means Clustering ($K=3$) | Inertia: 5438.45 | Silhouette: 0.2179 | 3 Clusters Discovered | Behavioral Segmentation | Applied |

*Evaluation conducted on 360 held-out test records (80/20 train/test split, 1,800 total samples).*

---

## 4. 'Earn Your Premium' Pedagogical Access Control Policy

Traditional Duolingo subscriptions rely on credit card checkouts and paywalls. In this project, all commercial Stripe dependencies were completely decoupled. Students earn **Super Pass / Legendary Access** purely through academic merit:

| Pedagogical Metric | Qualification Threshold | Purpose |
| :--- | :--- | :--- |
| **ML Mastery Prediction** | $\ge \text{Intermediate}$ or $\text{Advanced}$ | Verifies demonstrated comprehension |
| **Learning Consistency** | $\ge 65\%$ session regular participation | Rewards study habit and commitment |
| **Recent Quiz Accuracy** | $\ge 70\%$ correct answer rate | Ensures solid concept retention |
| **Performance Trajectory** | $\Delta \ge 0.0\%$ (Improvement or high-score maintenance) | Prevents negative student stagnation |

When criteria are satisfied, the system issues a **7-Day Legendary Pass** unlocking **Unlimited Hearts** and **AI Review Drills** directly in the database.

---

## 5. Instructions to Reproduce Training and Run System

### Step 1: Generate Dataset & Train Models
```bash
# In the repository root
& "ml_backend/venv/Scripts/python.exe" ml_backend/src/dataset_generator.py
& "ml_backend/venv/Scripts/python.exe" ml_backend/src/train.py
```
This generates:
- `ml_backend/data/student_performance.csv` (1,800 records)
- `ml_backend/models/best_model.pkl` (Serialized Logistic Regression)
- `ml_backend/models/preprocessor.pkl` (Serialized Z-Score & One-Hot Transformer)
- `ml_backend/models/kmeans_model.pkl` (Serialized K-Means Clusterer)
- `ml_backend/notebooks/model_comparison_report.json`
- `ml_backend/notebooks/confusion_matrix.svg`
- `ml_backend/notebooks/model_comparison.svg`

### Step 2: Start Python ML Microservice
```bash
& "ml_backend/venv/Scripts/python.exe" ml_backend/main.py
```
Active on `http://127.0.0.1:8000`. Endpoints:
- `GET  /health` — Verifies model readiness
- `POST /predict` — Evaluates telemetry into mastery level
- `POST /recommend` — Generates personalized learning path
- `POST /premium-eligibility` — Checks qualification criteria
- `POST /evaluate-session` — Composite pipeline for Next.js quiz completion
- `GET  /analytics/summary` — Full comparison report

### Step 3: Run Next.js Frontend
```bash
npm run dev
```
Open `http://localhost:3000`.
- Complete a lesson under `/learn`.
- View the real-time **ML Evaluation Card** on quiz completion.
- Open **Learning Intelligence** (`/intelligence`) to inspect the mastery dashboard and behavioral cluster.
- Open **Earn Premium** (`/shop`) to track criteria progress and activate your merit-based pass.

