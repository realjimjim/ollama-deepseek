from flask import Flask, render_template, request, Response, jsonify
import ollama
import os

app = Flask(__name__)

# Use a thread-safe way to pass messages
latest_user_message = None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    global latest_user_message
    user_message = request.json.get("message", "").strip()
    
    if not user_message:
        return jsonify({"error": "Message cannot be empty"}), 400

    latest_user_message = {"role": "user", "content": user_message}
    return jsonify({"status": "Message received"}), 200

@app.route("/stream")
def stream():
    global latest_user_message
    if not latest_user_message:
        yield "data: Error: No message\n\n"
        return

    def generate():
        temp_messages = [
            {"role": "system", "content": "You are a friendly and simple AI."},
            latest_user_message
        ]

        try:
            stream = ollama.chat(
                model="qwen2:0.5b",
                messages=temp_messages,
                options={
                    "temperature": 1,
                    "top_k": 1,
                    "top_p": 0.05,
                    "num_ctx": 2048
                },
                stream=True
            )

            buffer = ""
            found_think_end = False  # Set to True if you want to skip <think>

            for chunk in stream:
                text = chunk['message']['content']

                if not found_think_end:
                    buffer += text
                    if "</think>" in buffer:
                        found_think_end = True
                        buffer = buffer.split("</think>", 1)[-1].strip()
                        if buffer:
                            yield f"data: {buffer.replace(chr(10), '<br>')}\n\n"
                    continue

                yield f"data: {text.replace(chr(10), '<br>')}\n\n"

        except Exception as e:
            yield f"data: Error: {str(e)}\n\n"

    return Response(generate(), content_type="text/event-stream")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)