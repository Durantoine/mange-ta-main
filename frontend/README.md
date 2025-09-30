# mange-ta-main-front

This service is containerized using Docker and UV for dependency management, with separate setups for development and production.

## Requirements

- Docker
- Docker Compose
- UV (installed inside the container)
- Python 3.11+ (optional for local dev tools)

**⚠️ _Important:_** Start Docker before running any commands in this project.

## Makefile Commands

### Development & Production

- **Build dev image:**

```bash
make build-dev
```

- **Build prod image:**

```bash
make build-prod
```

- **Start dev environment:**

```bash
make dev-up
```

- **Start prod environment:**

```bash
make prod-up
```

- **Stop all containers:**

```bash
make stop
```

> **Tip:** Always build the image first if you’ve added new files, otherwise tools like Black or MyPy may not see them inside the container.

---

### Code Quality & Testing

- **Lint code with Ruff:**

```bash
make lint
```

- **Format code with Black:**

```bash
make format
```

- **Check types with MyPy:**

```bash
make check-types
```

- **Run tests with Pytest:**

```bash
make test
```

- **Run all checks (build first):**

```bash
make lint-all
```

> **Important:** If you add new files to `service/` or `tests/`, run `make build-dev` first. This ensures the container sees the new files before formatting, linting, or type-checking.

---

### Project Structure

```
├─ service/           # Python source code
│   └─ __init__.py
├─ tests/             # Test files
│   ├─ __init__.py
│   └─ fixtures.py
├─ pyproject.toml     # Project metadata and dependencies
├─ uv.lock            # Locked dependencies
├─ Dockerfile         # Dev & prod images
├─ compose.yaml       # Dev Compose configuration
├─ compose-prod-override.yaml # Prod overrides
├─ Makefile           # Common commands
```

---

### Notes

- The `tests/` folder must contain at least an `__init__.py` or a test file, otherwise the container may not see it.
- Dev environment mounts your source directories by default, so changes are reflected immediately.
- Prod environment only includes production dependencies and does not mount local files.
- Use `make stop` to safely stop all containers.
