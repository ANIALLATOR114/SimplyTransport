#!/bin/bash

# Pull latest code, sync Python deps, then restart the app via Supervisor

cd /home/niall/SimplyTransport
git pull

echo "Updating Python dependencies..."
source venv/bin/activate
uv pip install -r requirements-top-level.txt

echo "Restarting Supervisor..."
supervisorctl restart simplytransport