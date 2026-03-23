#!/usr/bin/env bash
# RED-AI Dry-Run Demo
# Run this script to see RED-AI's dry-run output across all categories.
# No root required — nothing is executed.
set -euo pipefail

echo "=== RED-AI Dry-Run Demo ==="
echo ""

COMMANDS=(
    "disable transparent hugepages"
    "set vm.swappiness to 10"
    "disable selinux"
    "open port 443 in firewall"
    "create a new user"
    "check disk space"
    "start and enable httpd"
    "configure network bonding"
    "install chrony for ntp"
    "check kernel version"
)

for cmd in "${COMMANDS[@]}"; do
    echo "---------------------------------------"
    echo "Prompt: \"$cmd\""
    echo ""
    red-ai --dry-run "$cmd" 2>/dev/null || echo "  (no match)"
    echo ""
done

echo "=== Demo Complete ==="
