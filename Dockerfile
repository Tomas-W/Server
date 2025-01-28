# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p db src/uploads/profile_pictures src/uploads/profile_icons

# Set environment variables
ENV FLASK_APP=run:get_app
ENV FLASK_ENV=deploy
ENV PORT=8080

# Run the application
CMD gunicorn run:app --bind 0.0.0.0:$PORT 