# ==========================================
# Stage 1: Build Frontend (Svelte + Vite)
# ==========================================
FROM node:22-alpine AS frontend-builder

WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# ==========================================
# Stage 2: Backend (FastAPI + SQLite)
# ==========================================
FROM python:3.13-slim

WORKDIR /app

# Prevent Python from writing .pyc and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATA_DIR=/app/data \
    UPLOAD_DIR=/app/uploads \
    FRONTEND_DIST=/app/frontend_dist

# Install dependencies
COPY backend/requirements.txt /app/backend/
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy backend source
COPY backend /app/backend

# Copy compiled frontend from Stage 1
COPY --from=frontend-builder /app/frontend/dist /app/frontend_dist

# Create persistent storage directories
RUN mkdir -p /app/data /app/uploads

EXPOSE 8000

VOLUME ["/app/data", "/app/uploads"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "/app/backend", "--proxy-headers", "--forwarded-allow-ips=*"]
