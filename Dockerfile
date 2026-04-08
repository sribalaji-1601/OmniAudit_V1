# Meta OpenEnv Hackathon compliant environment
# Environment variables needed:
# - API_BASE_URL: LLM API endpoint
# - MODEL_NAME: Model to use (e.g., gpt-3.5-turbo)
# - HF_TOKEN: API key for LLM service

FROM python:3.10-slim
WORKDIR /app
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 7860
CMD ["python", "server/app.py"]