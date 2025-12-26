FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt ./requirements-base.txt
COPY backend/requirements.txt ./requirements-backend.txt
RUN pip install --no-cache-dir -r requirements-base.txt -r requirements-backend.txt

# Copy application code
COPY core/ ./core/
COPY data/ ./data/
COPY simulation/ ./simulation/
COPY backend/ ./backend/

# Create data cache directory
RUN mkdir -p /app/data_cache

# Set Python path
ENV PYTHONPATH=/app

EXPOSE 8080

CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8080"]
