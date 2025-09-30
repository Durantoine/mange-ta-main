FROM python:3.13-slim AS base
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH"

FROM base AS dev
COPY . /app
RUN uv sync
ENTRYPOINT []
CMD ["python", "-m", "uvicorn", "service.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

FROM base AS prod
COPY . /app
RUN uv sync --no-dev
ENTRYPOINT []
CMD ["/app/.venv/bin/uvicorn", "service.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]