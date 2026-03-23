#!/usr/bin/env python3
"""Example: How to add a new command pattern to RED-AI's local database.

This script demonstrates the structure of a LOCAL_COMMANDS entry
and validates it against the schema.
"""
import json

# Example command pattern to add to red_ai/local_commands.py
new_pattern = {
    "keywords": ["configure", "chrony", "ntp", "time", "sync"],
    "description": "Configure chrony for NTP time synchronization",
    "category": "services",
    "commands": [
        "yum install -y chrony",
        "systemctl enable --now chronyd",
        "chronyc sources -v",
    ],
    "risk_level": "low",
    "requires_reboot": False,
    "notes": "Chrony replaces ntpd on RHEL 8/9.",
}

# Validate required fields
required = ["keywords", "description", "category", "commands", "risk_level", "requires_reboot"]
for field in required:
    assert field in new_pattern, "Missing required field: {}".format(field)

# Validate types
assert isinstance(new_pattern["keywords"], list), "keywords must be a list"
assert all(k == k.lower() for k in new_pattern["keywords"]), "keywords must be lowercase"
assert new_pattern["risk_level"] in ("low", "medium", "high"), "invalid risk_level"
assert isinstance(new_pattern["commands"], list) and len(new_pattern["commands"]) >= 1, "need at least 1 command"

print("Pattern is valid!")
print(json.dumps(new_pattern, indent=2))
print("\nAdd this to LOCAL_COMMANDS in red_ai/local_commands.py")
print("Then add a matching training example to Modelfile")
