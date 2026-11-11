#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

case "${1:-}" in
    metamapper)
        SERVICE_DIR="$REPO_DIR/metamapper"
        ENVIRONMENTS="local,gcp,local-gcs"
        ;;
    dispatcher)
        SERVICE_DIR="$REPO_DIR/metamapper-dispatcher"
        ENVIRONMENTS="local"
        ;;
    datadoc)
        SERVICE_DIR="$REPO_DIR/datadoc-service"
        ENVIRONMENTS="local"
        ;;
    *)
        echo "Usage: $0 {metamapper|dispatcher|datadoc}" >&2
        exit 1
        ;;
esac

cd "$SERVICE_DIR"

export MICRONAUT_ENVIRONMENTS="$ENVIRONMENTS"

exec ./gradlew run
