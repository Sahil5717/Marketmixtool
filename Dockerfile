FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python deps
# Install core deps first (always succeed), then optional deps (may fail)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir numpy pandas scipy scikit-learn fastapi uvicorn python-multipart openpyxl statsmodels && \
    pip install --no-cache-dir prophet || echo "Prophet not installed — linear fallback active" && \
    pip install --no-cache-dir pymc arviz || echo "PyMC not installed — OLS fallback active" && \
    pip install --no-cache-dir reportlab python-pptx || echo "Export libs not installed"

# Copy application code
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY templates/ ./templates/
COPY docs/ ./docs/
COPY LICENSE ./

# Set working directory to backend
WORKDIR /app/backend

# Expose port (Railway uses PORT env var)
EXPOSE 8000

# Start server
CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}"]
