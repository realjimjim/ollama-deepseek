from flask import Flask, render_template, request, Response, jsonify
import ollama
import os

app = Flask(__name__)
_chat_history = [{"role": "system", "content": "Friendly and Short replies only."}]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    global _chat_history
    msg = request.json.get("message", "").strip()
    if not msg:
        return jsonify({"error": "empty"}), 400

    _chat_history.append({"role": "user", "content": msg})
    if len(_chat_history) > 11:
        _chat_history = [_chat_history[0]] + _chat_history[-10:]

    return jsonify({"status": "ok"})

@app.route("/stream")
def stream():
    global _chat_history

    def generate():
        try:
            stream = ollama.chat(
                model="phi3:mini",  # ← Faster model
                messages=_chat_history,
                stream=True,
                options={
                    "num_ctx": 2048,
                    "num_predict": 256,
                    "temperature": 0.7,
                    "num_thread": 4,
                    "num_batch": 512,
                    "flash_attn": True,
                },
            )

            for chunk in stream:
                text = chunk["message"]["content"]
                yield f"data: {text.replace(chr(10), '<br>')}\n\n"

            # Append assistant reply to history
            full_reply = "".join([c["message"]["content"] for c in stream])
            _chat_history.append({"role": "assistant", "content": full_reply})

        except Exception as e:
            yield f"data: [error] {str(e)}\n\n"

    return Response(generate(), mimetype="text/event-stream")

@app.route("/health")
def health():
    return "OK", 200, {"Content-Type": "text/plain"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)