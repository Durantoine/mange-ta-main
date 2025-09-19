FROM python:3.13-slim AS base

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# UV environment settings
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_TOOL_BIN_DIR=/usr/local/bin
ENV PATH="/app/.venv/bin:$PATH"

# Copy only project metadata for dependency install
COPY pyproject.toml uv.lock* /app/

# Generate uv.lock if it doesn't exist
RUN --mount=type=cache,target=/root/.cache/uv \
    if [ ! -f uv.lock ]; then \
        echo "uv.lock not found — generating..."; \
        uv lock; \
    fi && \
    uv sync --locked --no-install-project


FROM base AS dev

# Install dev dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project

# Copy full project source
COPY . /app

# Install project itself + dev dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project

# Reset ENTRYPOINT
ENTRYPOINT []

# Dev CMD with fastapi CLI and hot reload
CMD ["python", "-m", "uvicorn", "service.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


FROM base AS prod

# Install only production dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --no-dev

# Copy full project source
COPY . /app

# Install project itself (prod only, no dev dependencies)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# Reset ENTRYPOINT
ENTRYPOINT []

# Prod CMD with uvicorn multi-worker
CMD ["/app/.venv/bin/uvicorn", "service:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]


