# mange_ta_main

[![Python](https://img.shields.io/badge/python-3.11+-blue)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen)](https://www.docker.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-backend-success)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-frontend-orange)](https://streamlit.io/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/)
[![Coverage](https://img.shields.io/badge/coverage-80%25-yellowgreen)](https://github.com/)
[![Pyright](https://img.shields.io/badge/type%20check-Pyright-blue)](https://github.com/)
[![Ruff](https://img.shields.io/badge/lint-Ruff-orange)](https://github.com/)

A **multi-service project** with a **FastAPI backend** and a **Streamlit frontend**, containerized with **Docker** and using **UV** for dependency management.

---

## Requirements

- Docker 20+ and Docker Compose 2+
- Python 3.11+ (optional for local dev tools)

**⚠️ Important:** Make sure Docker is running before executing any commands.

---

## Project Structure

```
├─ backend/                   # FastAPI backend
│   ├─ Dockerfile
│   ├─ Makefile
│   ├─ pyproject.toml
│   ├─ compose-backend.yaml
│   ├─ compose-backend-prod-override.yaml
│   ├─ service/               # Backend source code
│   └─ tests/                 # Backend tests
├─ frontend/                  # Streamlit frontend
│   ├─ Dockerfile
│   ├─ Makefile
│   ├─ pyproject.toml
│   ├─ compose-front.yaml
│   ├─ compose-front-prod-override.yaml
│   ├─ service/               # Frontend source code
│   └─ tests/                 # Frontend tests
├─ compose.yaml               # Global Compose dev config
├─ compose-prod-override.yaml # Global Compose prod override
├─ Makefile                   # Global Makefile
├─ EDA/                       # Data exploration notebooks
├─ LICENSE
└─ README.md
```

---

## Global Commands (All Services)

| Command                              | Description                                           |
| ------------------------------------ | ----------------------------------------------------- |
| `make service-dev-up`                | Build and start **all services** in development mode |
| `make service-prod-up`               | Build and start **all services** in production mode  |
| `make service-stop`                  | Stop all running containers                           |
| `make service-clean` / `make clean` | Stop all containers and prune unused Docker resources |

> The global Makefile orchestrates both backend and frontend using the global docker-compose configuration.

---

## Backend Commands (`backend/` folder)

| Command            | Description                                                                            |
| ------------------ | -------------------------------------------------------------------------------------- |
| `make build-dev`   | Build development image                                                                |
| `make build-prod`  | Build production image                                                                 |
| `make dev-up`      | Start dev environment with **hot reload** (live updates happen automatically inside the container) |
| `make prod-up`     | Start prod environment                                                                 |
| `make stop`        | Stop containers                                                                        |
| `make lint`        | Run **Ruff** linting                                                                   |
| `make lint-fix`    | Run **Ruff** and auto-fix issues                                                      |
| `make format`      | Format code with **Black** and **isort**                                              |
| `make check-types` | Type check with **Pyright**                                                            |
| `make test`        | Run **Pytest** tests with coverage reporting                                           |
| `make lint-all`    | Run all linting, formatting, and type checks                                           |

> **Tip:** Development is done **directly inside Docker containers**. With mounted volumes and live file synchronization, code changes on your host machine are reflected **immediately** — no need to rebuild the dev image for code edits.

---

## Frontend Commands (`frontend/` folder)

| Command            | Description                                                          |
| ------------------ | -------------------------------------------------------------------- |
| `make build-dev`   | Build development image                                              |
| `make build-prod`  | Build production image                                               |
| `make dev-up`      | Start dev environment with **hot reload** (changes update live)      |
| `make prod-up`     | Start prod environment                                               |
| `make stop`        | Stop containers                                                      |
| `make lint`        | Run **Ruff** linting                                                 |
| `make lint-fix`    | Run **Ruff** and auto-fix issues                                      |
| `make format`      | Format code with **Black** and **isort**                              |
| `make check-types` | Type check with **Pyright**                                          |
| `make test`        | Run **Pytest** tests with coverage reporting                         |
| `make lint-all`    | Run all linting, formatting, and type checks                         |

> Frontend also supports **live development inside Docker containers**. Changes to source files are synchronized in real-time via mounted volumes, allowing instant feedback without rebuilding images.

---

## Service Ports

| Service  | Port |
| -------- | ---- |
| Backend  | 8000 |
| Frontend | 8501 |

> Frontend automatically connects to the backend using `BACKEND_URL=http://mange_ta_main:8000` in development mode.

---

## Notes

- Each service has its own **Makefile**, **Dockerfile**, and **docker-compose**.  
- Global Makefile can orchestrate all services.  
- Backend container: `FastAPI` app with **live development** in dev mode.  
- Frontend container: `Streamlit` app with **live development** in dev mode.  
- Always stop containers before cleaning or rebuilding: `make service-stop`.  
- Dev environment mounts allow instant code updates; prod builds are immutable.

---

## Examples

### Start Full Project (Dev)
```bash
make service-dev-up
```

### Start Full Project (Prod)
```bash
make service-prod-up
```

### Run Backend Tests
```bash
cd backend
make test
```

### Run Frontend Tests
```bash
cd frontend
make test
```

### Clean Everything
```bash
make service-clean
```