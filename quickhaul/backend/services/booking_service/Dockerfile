FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/booking_service/ ./services/booking_service/
COPY shared/ ./shared/
COPY data/ ./data/

CMD ["uvicorn", "services.booking_service.app:app", "--host", "0.0.0.0", "--port", "8003"]
