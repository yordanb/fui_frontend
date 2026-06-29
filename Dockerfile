FROM python:3.12-slim

# Install system deps + curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-dev \
    gcc \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgobject-2.0-0 \
    libffi-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 --gid 1001 --no-create-home appuser

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt && \
    rm -rf /root/.cache/pip

COPY --chown=appuser:appgroup . .

EXPOSE 3005

USER appuser

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:3005", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-"]
