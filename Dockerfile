FROM python:3.11-slim

WORKDIR /app

# Install system dependencies required by Playwright/Chromium
RUN apt-get update && apt-get install -y \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
    libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
    libgbm1 libasound2 libpango-1.0-0 libcairo2 libx11-6 libxext6 \
    fonts-liberation wget --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Install google-genai first, then the rest — avoids namespace conflict with google-auth
RUN pip install --no-cache-dir google-genai>=1.0.0 && \
    pip install --no-cache-dir -r requirements.txt && \
    playwright install chromium

COPY . .

CMD ["sh", "-c", "exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
