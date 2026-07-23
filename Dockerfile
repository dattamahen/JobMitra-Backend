FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
# Install google-genai first, then the rest — avoids namespace conflict with google-auth
RUN pip install --no-cache-dir google-genai>=1.0.0 && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
