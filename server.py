from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Groq key (stored in Render env, NOT GitHub)
GROQ_KEY = os.getenv("GROQ_API_KEY")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


# ===============================
# Health Check (NEW)
# ===============================
@app.route("/", methods=["GET"])
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "AI Security Backend",
        "ai_enabled": bool(GROQ_KEY)
    })


# ===============================
# Analyze Endpoint
# ===============================
@app.route("/analyze", methods=["POST", "GET"])
def analyze():

    # If browser calls GET → show info
    if request.method == "GET":
        return jsonify({
            "message": "Use POST with JSON { prompt: '...' }",
            "status": "ready"
        })

    # POST logic
    data = request.json or {}
    prompt = data.get("prompt", "")

    if not prompt:
        return jsonify({"error": "Missing prompt"}), 400

    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": "You are a security analysis assistant"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 300
    }

    try:
        r = requests.post(
            GROQ_URL,
            json=payload,
            headers=headers,
            timeout=20
        )

        return jsonify(r.json())

    except Exception as e:
        return jsonify({
            "error": "Groq request failed",
            "details": str(e)
        }), 500


# ===============================
# Run Server
# ===============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
