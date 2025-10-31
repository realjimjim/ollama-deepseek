FROM python:3.11-slim

# Install Ollama binary
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://ollama.com/install.sh | sh && \
    rm -rf /var/lib/apt/lists/*

# Set up app
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# === FIX: Start Ollama server, then pull model ===
RUN ollama serve & \
    sleep 10 && \
    ollama pull deepseek-coder && \
    pkill ollama  # Optional: stop after pull (saves memory)

# === OR use a smaller model to avoid timeout (RECOMMENDED) ===
# RUN ollama serve & sleep 10 && ollama pull llama3.2:1b && pkill ollama

# Ollama config
ENV OLLAMA_HOST=0.0.0.0:11434
ENV PORT=10000
EXPOSE $PORT

# Start Ollama + Flask at runtime
CMD ollama serve & sleep 10 && python web.py