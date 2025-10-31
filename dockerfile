FROM python:3.11-slim

# Install Ollama + killall
RUN apt-get update && apt-get install -y curl procps && \
    curl -fsSL https://ollama.com/install.sh | sh && \
    rm -rf /var/lib/apt/lists/*

# Set up app
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# === FIX: Start Ollama, pull model, stop with killall ===
RUN ollama serve & \
    sleep 10 && \
    ollama pull phi3:mini && \
    killall ollama

# Ollama config
ENV OLLAMA_HOST=0.0.0.0:11434
ENV PORT=10000
ENV OLLAMA_MAX_LOADED_MODELS=1
ENV OLLAMA_KEEP_ALIVE=1m
ENV OLLAMA_NUM_PARALLEL=1
ENV OLLAMA_FLASH_ATTENTION=1
ENV OLLAMA_KV_CACHE_TYPE=q4_0
ENV OLLAMA_MAX_QUEUE=10
ENV OLLAMA_CONTEXT_LENGTH=2048
EXPOSE $PORT

# Runtime: Start Ollama + Flask
CMD ollama serve & sleep 10 && python web.py