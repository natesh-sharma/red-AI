import os
import json
import datetime

LOG_DIR = "/var/log/red-ai"
LOG_FILE = os.path.join(LOG_DIR, "executions.log")


def ensure_log_dir():
    os.makedirs(LOG_DIR, exist_ok=True)


def log_execution(prompt, commands, results, dry_run=False):
    try:
        ensure_log_dir()
    except PermissionError:
        return

    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "prompt": prompt,
        "commands": commands,
        "results": results,
        "dry_run": dry_run,
    }

    try:
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except PermissionError:
        pass
