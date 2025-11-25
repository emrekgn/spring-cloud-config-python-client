#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.integration.yml}"
SERVICE_NAME="${SERVICE_NAME:-config-server}"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cleanup() {
  docker compose -f "$COMPOSE_FILE" down --remove-orphans >/dev/null
}

trap cleanup EXIT

pushd "$PROJECT_DIR" >/dev/null

docker compose -f "$COMPOSE_FILE" up -d "$SERVICE_NAME"
python3 scripts/wait_for_config_server.py --url "http://localhost:8888/actuator/health"
CONFIG_SERVICE_HOST=localhost \
CONFIG_SERVICE_PORT=8888 \
CONFIG_USERNAME=config \
CONFIG_PASSWORD=config \
uv run pytest tests/integration
popd >/dev/null
