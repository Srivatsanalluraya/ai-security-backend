from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Your real Groq key (stored in server env, NOT GitHub)
GROQ_KEY = os.getenv("GROQ_API_KEY")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


@app.route("/analyze", methods=["POST"])
def analyze():

    data = request.json
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

    r = requests.post(GROQ_URL, json=payload, headers=headers)

    return jsonify(r.json())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
