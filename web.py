# web.py
from flask import Flask, render_template, request, Response, jsonify
import ollama
import os

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message", "").strip()
    if not user_msg:
        return jsonify({"error": "empty"}), 400

    # Truncate user message to 80 tokens (very safe)
    user_msg = " ".join(user_msg.split()[:80])

    # NO GLOBAL HISTORY — each request is isolated
    messages = [
        {"role": "system", "content": "Reply in under 50 words. Be concise."},
        {"role": "user", "content": user_msg}
    ]

    def stream_response():
        try:
            stream = ollama.chat(
                model="qwen2:0.5b-instruct-q4_0",  # Smaller quantized
                messages=messages,
                stream=True,
                options={
                    "num_ctx": 128,        # Only 128 tokens total context
                    "num_predict": 48,     # MAX 48 output tokens
                    "temperature": 0.7,
                },
            )

            for chunk in stream:
                text = chunk["message"]["content"]
                yield f"data: {text.replace(chr(10), '<br>')}\n\n"

            # Optional: force KV cache clear
            yield "data: [DONE]\n\n"

        except Exception as e:
            yield f"data: [error] {str(e)}\n\n"

    return Response(stream_response(), mimetype="text/event-stream")

@app.route("/health")
def health():
    return "OK", 200, {"Content-Type": "text/plain"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False, threaded=False)