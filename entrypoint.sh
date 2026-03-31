#!/bin/bash
set -e

echo "Configuring runner..."

./config.sh \
  --url $REPO_URL \
  --token $RUNNER_TOKEN \
  --name docker-runner \
  --work _work \
  --unattended \
  --replace

echo "Starting runner..."

exec ./run.sh