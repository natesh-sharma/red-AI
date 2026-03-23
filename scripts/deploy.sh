#!/usr/bin/env bash
# Deploy RED-AI to a RHEL target via SSH.
# Usage: ./scripts/deploy.sh <host> [--install]
set -euo pipefail

if [ $# -lt 1 ]; then
    echo "Usage: $0 <user@host> [--install]"
    echo ""
    echo "  <user@host>  SSH target (e.g., root@10.72.32.150)"
    echo "  --install    Install after copying (requires root)"
    echo ""
    echo "Examples:"
    echo "  $0 root@rhel-test        # Copy only"
    echo "  $0 root@rhel-test --install  # Copy and install"
    exit 1
fi

HOST="$1"
INSTALL="${2:-}"
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== Deploying RED-AI to $HOST ==="

# Sync project files
echo "[1/2] Copying files..."
rsync -avz --exclude='.git' --exclude='.venv' --exclude='__pycache__' \
    --exclude='*.egg-info' --exclude='dist' --exclude='build' \
    "$PROJECT_DIR/" "$HOST:/opt/red-ai/"

echo "  Files synced to $HOST:/opt/red-ai/"

if [ "$INSTALL" = "--install" ]; then
    echo "[2/2] Installing on remote..."
    ssh "$HOST" "cd /opt/red-ai && pip3 install -e . && echo 'Install OK'"
else
    echo "[2/2] Skipping install (use --install to install)"
fi

echo ""
echo "=== Deploy complete ==="
