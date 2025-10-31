FROM python:3.11-slim

# Install Ollama binary
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://ollama.com/install.sh | sh && \
    rm -rf /var/lib/apt/lists/*

# Set up Python app
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Pull your model (change 'deepseek-coder' if using something else)
RUN ollama pull deepseek-coder

# Make Ollama listen on all interfaces
ENV OLLAMA_HOST=0.0.0.0

# Expose port (Render sets $PORT automatically)
EXPOSE $PORT

# Start Ollama in background, wait a bit, then Flask
CMD ollama serve & sleep 10 && python web.py