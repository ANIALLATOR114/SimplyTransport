This folder contains sample configuration files for deploying the application on Linux.
This includes a config file for Nginx and Supervisor.

## Python version (3.14.3)

The canonical runtime is **Python 3.14.3**; [`pyproject.toml`](../pyproject.toml) allows **>=3.14.3,<3.15** (any security patch in the 3.14 line from 3.14.3 upward). Avoid pre-release alphas/betas in production. On the Ubuntu server:

1. Install Python (for example with [uv](https://github.com/astral-sh/uv): `uv python install 3.14.3`, or your preferred method such as the [deadsnakes](https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa) PPA if it provides 3.14.3).
2. From the project root, **recreate** the virtualenv used by Supervisor (see `supervisor_config.txt`, typically `venv` or `.venv`):

   ```bash
   rm -rf venv
   uv venv --python 3.14.3 venv
   source venv/bin/activate
   uv pip install -r requirements-top-level.txt
   ```

3. Ensure system packages for building or linking native extensions remain installed when wheels are missing (see **PostgreSQL client on Ubuntu** below).
4. Reload the app: `supervisorctl restart simplytransport` (or your equivalent).

### PostgreSQL client on Ubuntu (`psycopg2`)

Requirements list **`psycopg2-binary` only**. In the past, some setups added both `psycopg2` and `psycopg2-binary`; that is unnecessary—they ship the same Python module, and the plain `psycopg2` line often forces a **source build** that fails until PostgreSQL dev headers are present.

**Recommended on Ubuntu before `pip` / `uv pip install`:**

```bash
sudo apt update
sudo apt install -y libpq-dev
```

If anything still compiles C extensions (unusual when wheels exist), add build tools:

```bash
sudo apt install -y build-essential python3-dev
```

Then install app dependencies from the project root as usual. With `libpq-dev` installed, a fallback source build of the client can succeed; with a matching **wheel** for your Python version, `psycopg2-binary` installs without compiling.

`deploy.sh` only runs `git pull` and restarts Supervisor; it does not upgrade Python or reinstall dependencies—do that after pulling when you change the runtime version.
