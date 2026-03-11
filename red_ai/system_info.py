import os
import platform
import subprocess


def get_rhel_version():
    try:
        with open("/etc/redhat-release") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None


def get_system_info():
    info = {
        "hostname": platform.node(),
        "kernel": platform.release(),
        "arch": platform.machine(),
        "rhel_version": get_rhel_version(),
        "is_root": os.geteuid() == 0,
    }

    try:
        result = subprocess.run(
            ["getenforce"], capture_output=True, text=True, timeout=5
        )
        info["selinux"] = result.stdout.strip() if result.returncode == 0 else "unknown"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        info["selinux"] = "unknown"

    try:
        result = subprocess.run(
            ["systemctl", "is-active", "firewalld"],
            capture_output=True, text=True, timeout=5,
        )
        info["firewalld"] = result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        info["firewalld"] = "unknown"

    return info


def format_system_context(info):
    lines = [
        f"Hostname: {info['hostname']}",
        f"Kernel: {info['kernel']}",
        f"Arch: {info['arch']}",
        f"RHEL Version: {info['rhel_version'] or 'Not RHEL'}",
        f"Running as root: {info['is_root']}",
        f"SELinux: {info['selinux']}",
        f"Firewalld: {info['firewalld']}",
    ]
    return "\n".join(lines)
