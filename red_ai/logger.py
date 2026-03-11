import os
import pwd
import json
import datetime

LOG_DIR = "/var/log/red-ai"
LOG_FILE = os.path.join(LOG_DIR, "executions.log")


def ensure_log_dir():
    os.makedirs(LOG_DIR, exist_ok=True)


def log_execution(prompt, commands, results, dry_run=False,
                  source="unknown", risk_level="medium",
                  description="", requires_reboot=False, notes=""):
    try:
        ensure_log_dir()
    except PermissionError:
        return

    try:
        username = pwd.getpwuid(os.getuid()).pw_name
    except KeyError:
        username = str(os.getuid())

    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "user": username,
        "uid": os.getuid(),
        "hostname": os.uname().nodename,
        "prompt": prompt,
        "source": source,
        "description": description,
        "category": "",
        "risk_level": risk_level,
        "requires_reboot": requires_reboot,
        "dry_run": dry_run,
        "notes": notes,
        "commands_executed": [],
    }

    for r in results:
        cmd_entry = {
            "command": r.get("command", ""),
            "status": r.get("status", "unknown"),
            "output": r.get("output", "").strip(),
        }
        entry["commands_executed"].append(cmd_entry)

    try:
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except PermissionError:
        pass
