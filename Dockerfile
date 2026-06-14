# Use a slim Python 3.10 base image for minimal attack surface and fast deploys.
FROM python:3.10-slim

# Set working directory inside the container.
WORKDIR /app

# Install dependencies first (layering: rarely-changed layer caches well).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the full application source after dependencies to leverage Docker cache.
COPY . .

# Cloud Run supplies the PORT env var; default to 8080 for local compat.
ENV PORT=8080
ENV FLASK_ENV=production

EXPOSE 8080

# Use gunicorn for production-grade concurrent request handling.
CMD exec gunicorn --bind :$PORT --workers 2 run:app
