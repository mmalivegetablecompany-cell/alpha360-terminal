# Alpha360 Institutional Market Server Dockerfile
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8765

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code and databases
COPY backend ./backend
COPY database ./database
COPY dashboards ./dashboards
COPY live_price_server.py .

# Optional web build if serving Flutter web directly
COPY flutter_app/build/web ./flutter_app/build/web

EXPOSE 8765

CMD ["python", "live_price_server.py"]
