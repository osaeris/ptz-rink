# Python 3.11 is ONVIF-safe
FROM python:3.11-slim

# Prevent Python buffering (better logs)
ENV PYTHONUNBUFFERED=1

# Install system deps required by onvif-zeep
RUN apt-get update && apt-get install -y \
    libxml2 \
    libxslt1.1 \
    libffi8 \
    libssl3 \
    && rm -rf /var/lib/apt/lists/*

# App directory
WORKDIR /app

# Install Python deps first (for caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose Flask port
EXPOSE 5001

# Run app
CMD ["python", "app.py"]
