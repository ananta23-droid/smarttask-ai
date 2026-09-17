# Use an official lightweight Python runtime
FROM python:3.12-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Set working directory inside the container
WORKDIR /app

# Copy dependency definition first for optimal layer caching
COPY requirements.txt .

# Install dependencies without cache to keep the image lightweight
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application source code
# (.dockerignore ensures .env and development files are excluded)
COPY . .

# Expose default application port
EXPOSE 8000

# Start FastAPI application using uvicorn, binding to 0.0.0.0 and honoring $PORT
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
