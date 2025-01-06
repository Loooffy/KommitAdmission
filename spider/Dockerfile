FROM python:3.9-slim

WORKDIR /app

# Install system dependencies for scrapy
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

COPY .env .

CMD ["python", "app.py"] 