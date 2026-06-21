FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN groupadd -g 10001 appuser && useradd -u 10001 -g appuser -m -s /bin/bash appuser
COPY --chown=appuser:appuser services/otp_service/ ./services/otp_service/
COPY --chown=appuser:appuser shared/ ./shared/
COPY --chown=appuser:appuser data/ ./data/
USER 10001
CMD ["uvicorn", "services.otp_service.app:app", "--host", "0.0.0.0", "--port", "8005"]
