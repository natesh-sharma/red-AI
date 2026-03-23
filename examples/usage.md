# RED-AI Usage Examples

## Basic Dry-Run

Preview commands without executing them (no root required):

```bash
# Kernel tuning
red-ai --dry-run "disable transparent hugepages"
red-ai --dry-run "set vm.swappiness to 10"

# Security
red-ai --dry-run "disable selinux"
red-ai --dry-run "open port 443 in firewall"

# User management
red-ai --dry-run "create a new user"
red-ai --dry-run "add user to wheel group"

# Storage
red-ai --dry-run "extend lvm volume"
red-ai --dry-run "check disk space"

# Services
red-ai --dry-run "start and enable httpd"
red-ai --dry-run "configure kdump"

# Network
red-ai --dry-run "configure network bonding"
red-ai --dry-run "set static ip address"
```

## System Information

```bash
red-ai --info
```

Output:
```
System Information:
Hostname: rhel-server-01
Kernel: 4.18.0-372.el8.x86_64
Arch: x86_64
RHEL Version: Red Hat Enterprise Linux release 8.6 (Ootpa)
Running as root: True
SELinux: Enforcing
Firewalld: active
```

## Execution History

```bash
# Show last 10 executions
red-ai --history

# Show last 5 executions
red-ai --history 5
```

## Live Execution (Requires Root)

```bash
# With confirmation prompt
sudo red-ai "disable transparent hugepages"

# Skip confirmation (use with caution)
sudo red-ai --yes "check kernel version"
```

## Adding New Command Patterns

1. Edit `red_ai/local_commands.py`
2. Add entry to `LOCAL_COMMANDS` list:

```python
{
    "keywords": ["configure", "chrony", "ntp", "time", "sync"],
    "description": "Configure chrony for NTP time sync",
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
```

3. Add matching training example to `Modelfile`
4. Run tests: `python3 -m unittest discover -s tests -v`

## Building the RPM

```bash
./build_rpm.sh
# Output: dist/red-ai-2.0.0-1.el8.x86_64.rpm
```
