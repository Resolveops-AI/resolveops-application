# Stage 1: Build
FROM python:3.12-slim AS builder
WORKDIR /app
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"

RUN groupadd -g 10001 appuser && useradd -u 10001 -g appuser -m -s /bin/bash appuser
COPY --from=builder /opt/venv /opt/venv
COPY --chown=appuser:appuser services/auth_service/ ./services/auth_service/
COPY --chown=appuser:appuser shared/ ./shared/
COPY --chown=appuser:appuser data/ ./data/
USER 10001
CMD ["uvicorn", "services.auth_service.main:app", "--host", "0.0.0.0", "--port", "8002"]

# Trigger initial CI/CD build
