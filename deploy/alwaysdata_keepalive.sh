#!/usr/bin/env bash
set -euo pipefail

HEALTH_URL="${HEALTH_URL:-https://<your-domain>/health}"

curl --fail --silent --show-error --max-time 20 "$HEALTH_URL"
