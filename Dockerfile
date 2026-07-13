FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y \
    curl \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-xlib-2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn
COPY . .
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3005/health || exit 1
EXPOSE 3005
CMD ["gunicorn", "--bind", "0.0.0.0:3005", "--workers", "3", "app:app"]
