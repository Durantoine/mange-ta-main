FROM python:3.13-slim AS base
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app/frontend
ENV UV_LINK_MODE=copy
RUN apt-get update && apt-get install -y libatomic1 && rm -rf /var/lib/apt/lists/*

FROM base AS dev
COPY . /app
RUN uv sync
ENTRYPOINT []
CMD ["streamlit", "run", "service/app.py", "--server.port=8501", "--server.address=0.0.0.0"]

FROM base AS prod
COPY . /app
RUN uv sync --no-dev
ENTRYPOINT []
CMD ["streamlit", "run", "service/app.py", "--server.port=8501", "--server.address=0.0.0.0"]