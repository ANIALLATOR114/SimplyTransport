# AGENTS.md

## Cursor Cloud specific instructions

### Overview

SimplyTransport is a Litestar (Python 3.11) ASGI web app for Irish public transport data (GTFS & GTFS-R). It uses PostgreSQL, TimescaleDB, and Redis as backing services.

### Required services (Docker)

Start the three required services before running the app or tests:

```bash
sudo dockerd &>/dev/null &  # if not already running
sudo docker compose -f docker-compose.dev.yaml up -d postgres redis timescale
```

The optional OTel collector and Aspire dashboard are not needed for dev/test.

### Python virtual environment

The project requires Python 3.11. A venv lives at `/workspace/.venv`:

```bash
source /workspace/.venv/bin/activate
```

### Running the app

```bash
litestar run --host 0.0.0.0 --port 8000        # dev mode
litestar run --host 0.0.0.0 --port 8000 --reload  # with hot-reload
```

### Seeding test data

Import GTFS test fixtures and seed realtime data (pipe `y` to skip the interactive prompt):

```bash
echo "y" | litestar importgtfs -dir ./tests/gtfs_test_data/TFI/
litestar seedrealtimefromfile --file ./tests/gtfs_test_data/TFI/realtime_e2e_trip_updates.json --set-time-to-now
```

Use `--set-time-to-now` so stop times align with the current clock. The `GTFS_TFI_DATASET` env var must be `TFI` (already set in `.env`).

### Lint / format / type-check

See `README.md` for full details. Quick reference:

- `ruff check .` — lint
- `ruff format --check .` — format check
- `pyright` — type check (pre-existing errors in test mocks; not enforced in CI)

### Testing

```bash
python -m pytest
```

4 pre-existing test failures exist (statistics endpoints not seeded, one e2e realtime timing issue). All other ~285 tests pass.

### Non-obvious gotchas

- `litestar importgtfs` prompts interactively for confirmation — pipe `echo "y"` to automate.
- The `ENVIRONMENT=DEV` setting causes OTel export attempts to `localhost:4318`. Harmless "connection refused" warnings appear in logs/test output if the collector is not running. Set `ENVIRONMENT=PR-TEST-CI` to suppress.
- `psycopg2` requires `libpq-dev` system package to build from source.
- The `.env` file must exist — settings are loaded from it via `pydantic-settings`. Copy from `.env.example` if missing.
- Database tables are created via `litestar create_tables`, not Alembic migrations (Alembic is for incremental schema changes after initial setup).
