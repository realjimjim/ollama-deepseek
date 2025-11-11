# web.py
from flask import Flask, render_template, request, Response, jsonify
import ollama
import os

app = Flask(__name__)
_latest_msg = None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    global _latest_msg
    msg = request.json.get("message", "").strip()
    if not msg:
        return jsonify({"error": "empty"}), 400
    _latest_msg = {"role": "user", "content": msg}
    return jsonify({"status": "ok"})

@app.route("/stream")
def stream():
    global _latest_msg
    if not _latest_msg:
        def gen(): yield "data: [no message]\n\n"
        return Response(gen(), mimetype="text/event-stream")

    def generate():
        try:
            stream = ollama.chat(
                model="qwen2:0.5b",
                messages=[
                    {"role": "system", "content": "Short replies only."},
                    _latest_msg
                ],
                stream=True,
                options={
                    "num_ctx": 256,       # Critical: 256 tokens = ~6 MiB KV cache
                    "num_predict": 64,    # Max 64 output tokens
                    "temperature": 0.7,
                },
            )

            for chunk in stream:
                text = chunk["message"]["content"]
                yield f"data: {text.replace(chr(10), '<br>')}\n\n"

        except Exception as e:
            yield f"data: [error] {str(e)}\n\n"

    return Response(generate(), mimetype="text/event-stream")

@app.route("/health")
def health():
    return "OK", 200, {"Content-Type": "text/plain"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False, threaded=False)