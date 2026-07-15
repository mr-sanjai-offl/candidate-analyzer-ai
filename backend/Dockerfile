# ==============================================================================
# ApexGuidance AI Backend — Multi-stage Docker Build
# Architecture Bible Section 4: Docker containerization
# Architecture Bible Section 7: Python 3.12+
# ==============================================================================

# ---------------------------------------------------------------------------
# Stage 1: Builder — Install Python dependencies
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---------------------------------------------------------------------------
# Stage 2: Runtime — Minimal production image
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS runtime

# Security: create and run as non-root user
RUN groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid 1000 --create-home appuser

WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /install /usr/local

# Copy application source
COPY . .

# Set ownership to non-root user
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Health check (Architecture Section 12)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')"

# Run with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
