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
COPY services/payment_service/ ./services/payment_service/
COPY shared/ ./shared/

# Use uvicorn to run the service from the root to handle shared imports correctly
CMD ["uvicorn", "services.payment_service.main:app", "--host", "0.0.0.0", "--port", "8006"]
