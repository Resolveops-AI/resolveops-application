FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Ensure logs are sent straight to the terminal
ENV PYTHONUNBUFFERED=1

# Install system dependencies (needed for some Python packages)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all backend code
COPY . .
