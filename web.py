from flask import Flask, render_template, request, Response, jsonify
import ollama
import time

app = Flask(__name__)

messages = [{"role": "system", "content": "You are a friendly and simple AI."}]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    """Handles user input and starts AI response streaming."""
    user_message = request.json.get("message", "").strip()
    
    if not user_message:
        return jsonify({"error": "Message cannot be empty"}), 400

    # Store user message temporarily for the response
    global latest_user_message
    latest_user_message = {"role": "user", "content": user_message}

    return jsonify({"status": "Message received"}), 200

@app.route("/stream")
def stream():
    """Streams AI response in real-time, ignoring content before '</think>'."""
    def generate():
        global latest_user_message

        temp_messages = [
            {"role": "system", "content": "You are a friendly and simple AI."},
            latest_user_message
        ]

        stream = ollama.chat(
            model="deepseek-r1:1.5b",
            messages=temp_messages,
            options={"temperature": 1, "top_k": 1, "top_p": 0.05},
            stream=True
        )

        buffer = ""  # Store initial chunks to detect "</think>"
        found_think_end = True

        for chunk in stream:
            text = chunk['message']['content']

            if not found_think_end:
                buffer += text
                if "</think>" in buffer:
                    found_think_end = True
                    buffer = buffer.split("</think>", 1)[-1]  # Keep only content after `</think>`
                    buffer = buffer.strip()  # Remove leading/trailing spaces

                    if buffer:  # If there's content right after </think>, send it immediately
                        yield "data: {}\n\n".format(buffer.replace("\n", "<br>"))
                continue  # Skip yielding during thinking phase
            
            # Stream response normally after </think>
            yield "data: {}\n\n".format(text.replace("\n", "<br>"))

        messages.append({"role": "assistant", "content": buffer.strip()})  # Store the response

    return Response(generate(), content_type="text/event-stream")





if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))  # Get PORT from Render, default to 5000
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)
