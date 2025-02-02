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

# Create a non-root user
RUN useradd -m -r appuser && \
    chown -R appuser:appuser /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Switch to non-root user
USER appuser

# Create virtual environment and install dependencies
RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY --chown=appuser:appuser . .

# Create necessary directories
RUN mkdir -p db src/uploads/profile_pictures src/uploads/profile_icons

# Set environment variables
ENV FLASK_APP=run:get_app
ENV FLASK_ENV=deploy
ENV PYTHONUNBUFFERED=1

# Run the application with adjusted logging
CMD ["gunicorn", "run:app", "--bind=0.0.0.0:8080", "--timeout=180", "--workers=1", "--log-level=error", "--access-logfile=/dev/null", "--error-logfile=-", "--capture-output"] 