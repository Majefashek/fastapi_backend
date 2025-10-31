# Base image
FROM python:3.11-slim

# -------------------------------------------------------------------
# 💡 THE FIX FOR DOCKER
# This environment variable forces Python to print logs instantly
# instead of holding them in a buffer. This is essential for
# seeing logs in real-time.
# -------------------------------------------------------------------
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Copy dependencies
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Start FastAPI with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]