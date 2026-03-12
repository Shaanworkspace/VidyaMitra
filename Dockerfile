# VidyaMitra Career Agent - Production Docker Image
# Multi-stage build for optimized production deployment

# ================================
# Stage 1: Python Backend Build
# ================================
FROM python:3.11-slim as backend-builder

LABEL maintainer="VidyaMitra Team <shaanyadav1012004@gmail.com>"
LABEL description="VidyaMitra Career Agent - AI-powered resume optimization"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy Python requirements and install dependencies
COPY backend/requirements.txt backend/requirements-lock.txt ./
RUN pip install --no-cache-dir -r requirements-lock.txt

# ================================
# Stage 2: Node.js Frontend Build  
# ================================
FROM node:18-alpine as frontend-builder

WORKDIR /app/frontend

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci --only=production && npm cache clean --force

# Copy frontend source
COPY frontend/ ./

# Build frontend for production
RUN npm run build

# ================================
# Stage 3: Production Runtime
# ================================
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/backend \
    NODE_ENV=production \
    PORT=8000

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r vidyamitra \
    && useradd -r -g vidyamitra vidyamitra

# Create app directory and set permissions
WORKDIR /app
RUN chown -R vidyamitra:vidyamitra /app

# Copy Python dependencies from builder
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# Copy backend application
COPY backend/ ./backend/

# Copy built frontend
COPY --from=frontend-builder /app/frontend/out ./frontend/out
COPY --from=frontend-builder /app/frontend/public ./frontend/public

# Copy additional files
COPY requirements.txt pyproject.toml setup.py ./
COPY notebooks/ ./notebooks/
COPY data/ ./data/
COPY scripts/ ./scripts/

# Create necessary directories
RUN mkdir -p logs && \
    chown -R vidyamitra:vidyamitra /app

# Switch to non-root user
USER vidyamitra

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Default command
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]

# ================================
# Build Arguments & Metadata
# ================================
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION=1.0.0

LABEL org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.name="vidyamitra-career-agent" \
      org.label-schema.description="AI-powered resume optimization with semantic analysis" \
      org.label-schema.url="https://github.com/shaanyadav/vidyamitra-career-agent" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.vcs-url="https://github.com/shaanyadav/vidyamitra-career-agent" \
      org.label-schema.vendor="VidyaMitra Team" \
      org.label-schema.version=$VERSION \
      org.label-schema.schema-version="1.0"