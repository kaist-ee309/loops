# Build stage
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

# Set working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Copy dependency files first for better caching
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-install-project --no-dev

# Copy the rest of the project
COPY . .

# Sync the project (install the project itself)
RUN uv sync --frozen --no-dev


# Runtime stage
FROM python:3.12-slim-bookworm

# Set working directory
WORKDIR /app

# Create non-root user FIRST (before COPY --chown)
RUN useradd -m -u 1000 app

# Copy the application from builder
COPY --from=builder --chown=app:app /app /app

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Set PYTHONPATH to include src directory
ENV PYTHONPATH="/app/src"

# Switch to non-root user
USER app

# Expose port (Cloud Run uses PORT env var, default 8080)
EXPOSE 8080

# Cloud Run sets PORT env var, default to 8080
ENV PORT=8080

# Run the application with uvicorn
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
