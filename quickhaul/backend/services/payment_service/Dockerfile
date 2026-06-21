FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from the specific service folder
COPY services/payment_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the service and shared code
RUN groupadd -g 10001 appuser && useradd -u 10001 -g appuser -m -s /bin/bash appuser
COPY --chown=appuser:appuser services/payment_service/ ./services/payment_service/
COPY --chown=appuser:appuser shared/ ./shared/
USER 10001
CMD ["uvicorn", "services.payment_service.main:app", "--host", "0.0.0.0", "--port", "8006"]
