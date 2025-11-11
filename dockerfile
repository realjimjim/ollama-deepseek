FROM python:3.11-slim

# Install curl + procps (for killall if needed)
RUN apt-get update && apt-get install -y curl procps && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Set up app
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Environment variables
ENV OLLAMA_HOST=0.0.0.0:11434
ENV PORT=10000
ENV OLLAMA_MAX_LOADED_MODELS=1
ENV OLLAMA_KEEP_ALIVE=5m
ENV OLLAMA_NUM_PARALLEL=1
ENV OLLAMA_FLASH_ATTENTION=true
ENV OLLAMA_KV_CACHE_TYPE=q4_0
ENV OLLAMA_MAX_QUEUE=10
ENV OLLAMA_CONTEXT_LENGTH=2048

EXPOSE $PORT

# Start Ollama in background, pull model once, then run Flask
CMD ollama serve & \
    until ollama list | grep -q "qwen2:0.5b"; do \
        echo "Pulling qwen2:0.5b..."; \
        ollama pull qwen2:0.5b || true; \
        sleep 5; \
    done && \
    echo "Model ready. Starting Flask..." && \
    python web.py