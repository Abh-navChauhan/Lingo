"""
FASTAPI / HTTP REST MACHINE LEARNING MICROSERVICE
-------------------------------------------------
Statistical Machine Learning (SML) College Project - Duolingo Adaptive Learning Platform

Provides robust RESTful endpoints for real-time model inference,
adaptive pedagogical recommendations, and merit-based premium eligibility.
Supports both standard FastAPI/Uvicorn and built-in Python HTTP server with CORS.
"""

import os
import sys
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# Ensure ml_backend and ml_backend/src are on PYTHONPATH
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

import sml_models

from src.predict import predict_student_mastery, get_models
from src.recommendations import generate_recommendations
from src.premium import evaluate_premium_eligibility

PORT = 8000

class MLRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200, content_type="application/json"):
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(204)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/health" or path == "/":
            try:
                model, _, _ = get_models()
                model_ready = model is not None
            except Exception:
                model_ready = False

            payload = {
                "status": "healthy" if model_ready else "degraded",
                "service": "Lingo ML Adaptive Engine",
                "model_loaded": model_ready,
                "framework": "Statistical Machine Learning (SML)"
            }
            self._set_headers(200)
            self.wfile.write(json.dumps(payload).encode("utf-8"))

        elif path == "/analytics/summary":
            report_path = os.path.join(os.path.dirname(__file__), "notebooks", "model_comparison_report.json")
            if os.path.exists(report_path):
                with open(report_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._set_headers(200)
                self.wfile.write(json.dumps(data).encode("utf-8"))
            else:
                self._set_headers(200)
                self.wfile.write(json.dumps({"status": "pending_training"}).encode("utf-8"))

        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": f"Endpoint not found: {path}"}).encode("utf-8"))

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)

        try:
            body = json.loads(post_data.decode("utf-8")) if post_data else {}
        except Exception as e:
            self._set_headers(400)
            self.wfile.write(json.dumps({"error": f"Malformed JSON: {str(e)}"}).encode("utf-8"))
            return

        try:
            if path == "/predict":
                result = predict_student_mastery(body)
                response = {
                    "student_id": body.get("student_id", "guest"),
                    "topic": body.get("topic", "Spanish Basics"),
                    **result
                }
                self._set_headers(200)
                self.wfile.write(json.dumps(response).encode("utf-8"))

            elif path == "/recommend":
                mastery = body.get("predicted_mastery", "Intermediate")
                conf = float(body.get("confidence", 0.85))
                topic = body.get("current_topic", "Spanish Basics")
                topic_history = body.get("topic_history", None)
                recent_acc = float(body.get("recent_accuracy", 0.8))
                resp_time = float(body.get("avg_response_time", 15.0))

                recs = generate_recommendations(
                    predicted_mastery=mastery,
                    confidence=conf,
                    current_topic=topic,
                    topic_history=topic_history,
                    recent_accuracy=recent_acc,
                    avg_response_time=resp_time
                )
                self._set_headers(200)
                self.wfile.write(json.dumps(recs).encode("utf-8"))

            elif path == "/premium-eligibility":
                mastery = body.get("predicted_mastery", "Intermediate")
                conf = float(body.get("confidence", 0.85))
                consistency = float(body.get("learning_consistency", 0.8))
                improvement = float(body.get("recent_improvement", 0.05))
                acc = float(body.get("recent_accuracy", 0.8))
                attempts = int(body.get("number_of_attempts", 1))

                eligibility = evaluate_premium_eligibility(
                    predicted_mastery=mastery,
                    confidence=conf,
                    learning_consistency=consistency,
                    recent_improvement=improvement,
                    recent_accuracy=acc,
                    number_of_attempts=attempts
                )
                self._set_headers(200)
                self.wfile.write(json.dumps(eligibility).encode("utf-8"))

            elif path == "/evaluate-session":
                pred_res = predict_student_mastery(body)
                mastery = pred_res["predicted_mastery"]
                conf = pred_res["confidence"]

                recs = generate_recommendations(
                    predicted_mastery=mastery,
                    confidence=conf,
                    current_topic=body.get("topic", "Spanish Basics"),
                    topic_history=body.get("topic_history", None),
                    recent_accuracy=float(body.get("topic_wise_accuracy", body.get("previous_accuracy", 0.8))),
                    avg_response_time=float(body.get("avg_response_time", 15.0))
                )

                premium = evaluate_premium_eligibility(
                    predicted_mastery=mastery,
                    confidence=conf,
                    learning_consistency=float(body.get("learning_consistency", 0.8)),
                    recent_improvement=float(body.get("recent_improvement", 0.05)),
                    recent_accuracy=float(body.get("topic_wise_accuracy", body.get("previous_accuracy", 0.8))),
                    number_of_attempts=int(body.get("number_of_attempts", 1))
                )

                response = {
                    "prediction": pred_res,
                    "recommendations": recs,
                    "premium_eligibility": premium
                }
                self._set_headers(200)
                self.wfile.write(json.dumps(response).encode("utf-8"))

            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": f"Endpoint not found: {path}"}).encode("utf-8"))

        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": f"Internal ML error: {str(e)}"}).encode("utf-8"))

    def log_message(self, format, *args):
        # Concise logging to stdout
        sys.stdout.write(f"[{self.log_date_time_string()}] {self.address_string()} - {format % args}\n")
        sys.stdout.flush()

def run_server():
    server_address = ("127.0.0.1", PORT)
    httpd = HTTPServer(server_address, MLRequestHandler)
    print(f"=" * 70)
    print(f"Lingo ML Adaptive Learning Microservice running on http://127.0.0.1:{PORT}")
    print(f"Endpoints active: /health, /predict, /recommend, /premium-eligibility, /evaluate-session")
    print(f"=" * 70)
    sys.stdout.flush()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping ML server.")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
