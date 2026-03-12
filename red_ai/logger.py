import os
import pwd
import json
import glob
import datetime

LOG_DIR = "/var/log/red-ai"
LOG_FILE = os.path.join(LOG_DIR, "executions.log")
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5 MB
MAX_LOG_FILES = 3  # Keep 3 rotated files


def ensure_log_dir():
    os.makedirs(LOG_DIR, exist_ok=True)


def _rotate_logs():
    """Rotate log file if it exceeds MAX_LOG_SIZE.

    Keeps up to MAX_LOG_FILES rotated copies:
      executions.log -> executions.log.1 -> executions.log.2 -> (deleted)
    """
    try:
        if not os.path.exists(LOG_FILE):
            return
        if os.path.getsize(LOG_FILE) < MAX_LOG_SIZE:
            return
    except OSError:
        return

    # Remove oldest rotated file
    oldest = f"{LOG_FILE}.{MAX_LOG_FILES}"
    if os.path.exists(oldest):
        os.remove(oldest)

    # Shift existing rotated files
    for i in range(MAX_LOG_FILES - 1, 0, -1):
        src = f"{LOG_FILE}.{i}"
        dst = f"{LOG_FILE}.{i + 1}"
        if os.path.exists(src):
            os.rename(src, dst)

    # Rotate current log
    os.rename(LOG_FILE, f"{LOG_FILE}.1")


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

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    hostname = os.uname().nodename
    mode = "DRY RUN" if dry_run else "EXECUTED"

    # Build human-readable log entry
    lines = []
    lines.append("=" * 70)
    lines.append(f"  Timestamp  : {timestamp}")
    lines.append(f"  User       : {username} (uid={os.getuid()})")
    lines.append(f"  Hostname   : {hostname}")
    lines.append(f"  Mode       : {mode}")
    lines.append(f"  Source     : {source}")
    lines.append(f"  Risk Level : {risk_level}")
    lines.append(f"  Reboot Req : {'Yes' if requires_reboot else 'No'}")
    lines.append("-" * 70)
    lines.append(f"  Request    : {prompt}")
    lines.append(f"  Description: {description}")
    if notes:
        lines.append(f"  Notes      : {notes}")
    lines.append("-" * 70)

    for i, r in enumerate(results, 1):
        cmd = r.get("command", "")
        status = r.get("status", "unknown").upper()
        output = r.get("output", "").strip()

        lines.append(f"  [{i}] {cmd}")
        lines.append(f"      Status: {status}")
        if output:
            for out_line in output.split("\n"):
                lines.append(f"      > {out_line}")

    lines.append("=" * 70)
    lines.append("")

    try:
        _rotate_logs()
        with open(LOG_FILE, "a") as f:
            f.write("\n".join(lines) + "\n")
    except PermissionError:
        pass
