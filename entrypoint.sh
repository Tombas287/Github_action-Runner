#!/bin/bash
set -e

echo "Cleaning previous runner (if any)..."
./config.sh remove --unattended --token "$RUNNER_TOKEN" || true

echo "Configuring runner..."

./config.sh \
  --url "$REPO_URL" \
  --token "$RUNNER_TOKEN" \
  --work "_work" \
  --unattended \
  --replace \
  --ephemeral

echo "Starting runner..."

exec ./run.sh