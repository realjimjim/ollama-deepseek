FROM python:3.11-slim

# Install curl + procps
RUN apt-get update && apt-get install -y curl procps && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Environment
ENV OLLAMA_HOST=0.0.0.0:11434
ENV OLLAMA_MAX_LOADED_MODELS=1
ENV OLLAMA_KEEP_ALIVE=5m
ENV OLLAMA_NUM_PARALLEL=1
ENV OLLAMA_KV_CACHE_TYPE=q4_0
ENV OLLAMA_CONTEXT_LENGTH=256

EXPOSE $PORT

# Start Ollama, pull model (retry if needed), then Flask
CMD ollama serve & \
    sleep 10 && \
    echo "Pulling phi3:mini..." && \
    until ollama list | grep -q "phi3:mini"; do \
        ollama pull phi3:mini || echo "Retry in 5s..."; \
        sleep 5; \
    done && \
    echo "Model ready! Starting Flask on port $PORT..." && \
    python web.py