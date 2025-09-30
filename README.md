# mange_ta_main

A **multi-service project** with a **FastAPI backend** and a **Streamlit frontend**, containerized with **Docker** and using **UV** for dependency management.

## Requirements

- Docker
- Docker Compose
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

| Command                             | Description                                          |
| ----------------------------------- | ---------------------------------------------------- |
| `make service-dev-up`               | Build and start **all services** in development mode |
| `make service-prod-up`              | Build and start **all services** in production mode  |
| `make service-stop`                 | Stop all running containers                          |
| `make service-clean` / `make clean` | Stop all containers and prune system                 |

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
| `make format`      | Format code with **Black**, **isort**, **autopep8**                                    |
| `make check-types` | Type check with **Pyright**                                                            |
| `make test`        | Run **Pytest** tests                                                                   |
| `make lint-all`    | Run all linting, formatting, and type checks                                           |

> **Tip:** Development is done **directly inside Docker containers**. With mounted volumes and live file synchronization (via the container setup), code changes on your host machine are reflected **immediately** — no need to rebuild the dev image when adding or editing files.

---

## Frontend Commands (`frontend/` folder)

| Command            | Description                                                          |
| ------------------ | -------------------------------------------------------------------- |
| `make build-dev`   | Build dev image                                                      |
| `make build-prod`  | Build prod image                                                     |
| `make dev-up`      | Start dev environment with **hot reload** (changes are updated live) |
| `make prod-up`     | Start prod environment                                               |
| `make stop`        | Stop containers                                                      |
| `make lint`        | Run **Ruff** linting                                                 |
| `make format`      | Format code with **Black**, **isort**, **autopep8**                  |
| `make check-types` | Type check with **Pyright**                                          |
| `make test`        | Run **Pytest** tests                                                 |
| `make lint-all`    | Run all linting, formatting, and type checks                         |

> Both backend and frontend support **live development directly inside Docker containers**. Changes to source files are synchronized in real-time via mounted volumes, allowing instant feedback without rebuilding images.

---

## Service Ports

| Service  | Port |
| -------- | ---- |
| Backend  | 8000 |
| Frontend | 8501 |

> Frontend automatically connects to the backend using `BACKEND_URL=http://mange_ta_main:8000` in dev.

---

## Notes

- Each service has its own **Makefile**, **Dockerfile**, and **docker-compose**.
- Global Makefile can orchestrate all services.
- Backend container: `FastAPI` app, supports **live development** in dev mode.
- Frontend container: `Streamlit` app, supports **live development** in dev mode.
- Always stop containers before cleaning or rebuilding: `make service-stop`.
- Dev environment mounts allow instant code updates; prod builds are immutable.

---

## Example: Start Full Project (Dev)

```bash
make service-dev-up
```

## Example: Run Backend Tests

```bash
cd backend
make test
```

## Example: Run Frontend Tests

```bash
cd frontend
make test
```

