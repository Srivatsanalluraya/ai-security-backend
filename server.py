from flask import Flask, request, jsonify
import requests
import os
import time

app = Flask(__name__)

# Groq API key (stored in Render env, NOT GitHub)
GROQ_KEY = os.getenv("GROQ_API_KEY")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


# -------------------------
# Health Check (IMPORTANT)
# -------------------------
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "ai-security-backend",
        "time": time.time()
    }), 200


# -------------------------
# AI Analysis Endpoint
# -------------------------
@app.route("/analyze", methods=["POST"])
def analyze():

    if not GROQ_KEY:
        return jsonify({"error": "Groq API key not configured"}), 500

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

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
        # IMPORTANT: timeout added
        r = requests.post(
            GROQ_URL,
            json=payload,
            headers=headers,
            timeout=60
        )

        # If Groq fails
        if r.status_code != 200:
            return jsonify({
                "error": "Groq API failed",
                "status": r.status_code,
                "details": r.text[:500]
            }), 502

        return jsonify(r.json())

    except requests.exceptions.Timeout:
        return jsonify({"error": "Groq API timeout"}), 504

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------------
# Server Startup
# -------------------------
if __name__ == "__main__":

    port = int(os.getenv("PORT", 5000))  # Render sets PORT

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
