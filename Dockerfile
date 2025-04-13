# Use multi-stage build for smaller final image
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.11-slim

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user
RUN useradd -m -u 1000 mcp
USER mcp

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=mcp:mcp . .

# Environment variables
ENV PORT=8001
ENV HOST=0.0.0.0
ENV WORKERS=4

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:8001/health || exit 1

# Run the application with multiple workers
CMD ["sh", "-c", "uvicorn main:app --host $HOST --port $PORT --workers $WORKERS"] 