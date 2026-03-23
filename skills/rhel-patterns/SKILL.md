---
name: rhel-patterns
description: RHEL system administration command patterns for RED-AI's local_commands.py database. Covers command structure, categories, risk levels, and adding new patterns.
origin: red-ai
---

# RHEL Command Patterns for RED-AI

Reference for maintaining and extending RED-AI's local command database (230+ patterns) across all RHEL system administration categories.

## When to Activate

- Adding new command patterns to local_commands.py
- Reviewing keyword matching accuracy
- Categorizing commands by risk level
- Ensuring RHEL 7/8/9 cross-compatibility
- Training the Ollama model with new examples

## Command Entry Structure

Every entry in `LOCAL_COMMANDS` must follow this schema:

```python
{
    "keywords": ["disable", "transparent", "hugepages", "thp"],
    "description": "Disable transparent hugepages (runtime + persistent via grub)",
    "category": "kernel",
    "commands": [
        "echo never > /sys/kernel/mm/transparent_hugepage/enabled",
        "echo never > /sys/kernel/mm/transparent_hugepage/defrag",
        "grubby --update-kernel=ALL --args='transparent_hugepage=never'",
    ],
    "risk_level": "medium",       # "low", "medium", or "high"
    "requires_reboot": False,     # True if reboot needed
    "notes": "Runtime change is immediate. Grub change persists across reboots.",
}
```

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `keywords` | list[str] | Lowercase words for matching user queries |
| `description` | str | Human-readable description of what this does |
| `category` | str | Category grouping (see below) |
| `commands` | list[str] | Ordered shell commands to execute |
| `risk_level` | str | `"low"`, `"medium"`, or `"high"` |
| `requires_reboot` | bool | Whether a reboot is needed |
| `notes` | str | Additional context for the user |

## Categories

| Category | Description | Examples |
|----------|-------------|----------|
| `kernel` | Kernel modules, parameters, hugepages | modprobe, sysctl, grubby |
| `network` | Network config, firewall, DNS, bonding | nmcli, firewall-cmd, ip |
| `storage` | LVM, filesystems, disk, NFS, mounts | lvcreate, mkfs, mount, fstab |
| `security` | SELinux, firewall, SSH, passwords, audit | setenforce, authconfig, auditctl |
| `services` | Systemd services, targets, timers | systemctl, timedatectl |
| `users` | User/group management, sudo, PAM | useradd, groupmod, visudo |
| `packages` | Yum/DNF, repos, RPM management | yum, dnf, rpm, subscription-manager |
| `performance` | Tuning, profiling, resource limits | tuned, ulimit, nice |
| `logging` | Rsyslog, journald, log rotation | rsyslog, logrotate, journalctl |
| `monitoring` | System health, processes, resources | top, sar, iostat, vmstat |
| `boot` | GRUB, boot targets, rescue mode | grubby, systemctl set-default |
| `containers` | Podman, container management | podman, buildah, skopeo |
| `virtualization` | KVM, libvirt, virtual machines | virsh, virt-install |
| `backup` | Backup, restore, snapshots | tar, rsync, lvcreate --snapshot |

## Risk Level Guidelines

### Low Risk - Read-only or easily reversible
```python
"risk_level": "low"
# Examples:
# - Viewing system information (uname, lscpu, free)
# - Listing configurations (firewall-cmd --list-all)
# - Checking service status (systemctl status)
# - Reading logs (journalctl, cat /var/log/*)
```

### Medium Risk - System changes that are reversible
```python
"risk_level": "medium"
# Examples:
# - Starting/stopping services (systemctl restart)
# - Loading kernel modules (modprobe)
# - Changing sysctl parameters
# - Adding firewall rules
# - Creating users/groups
# - Installing packages
```

### High Risk - Potentially destructive or irreversible
```python
"risk_level": "high"
# Examples:
# - Disabling SELinux (setenforce 0 + config change)
# - Formatting filesystems (mkfs)
# - Removing LVM volumes (lvremove)
# - Modifying GRUB boot parameters
# - Deleting users with home directories
# - Resetting root password
# - Disabling firewall entirely
```

## Adding New Patterns

### Step 1: Identify the operation
```python
# What does the user want to do?
# "configure network bonding with two interfaces"
```

### Step 2: Research RHEL-compatible commands
```bash
# Verify commands work on RHEL 7, 8, AND 9
# RHEL 7: uses ifcfg scripts, network service
# RHEL 8: uses nmcli, NetworkManager
# RHEL 9: uses nmcli, NetworkManager (ifcfg deprecated)
```

### Step 3: Choose keywords carefully
```python
# Include common synonyms and abbreviations
"keywords": ["configure", "network", "bonding", "bond", "nic", "teaming"]
# - Use lowercase only
# - Include the action verb (configure, create, enable, disable)
# - Include the subject (network, bonding, bond)
# - Include common aliases (nic, teaming)
```

### Step 4: Write the entry
```python
{
    "keywords": ["configure", "network", "bonding", "bond", "nic"],
    "description": "Configure network bonding (active-backup) with two interfaces",
    "category": "network",
    "commands": [
        "nmcli connection add type bond con-name bond0 ifname bond0 mode active-backup",
        "nmcli connection add type ethernet con-name bond0-slave1 ifname <nic1> master bond0",
        "nmcli connection add type ethernet con-name bond0-slave2 ifname <nic2> master bond0",
        "nmcli connection up bond0",
    ],
    "risk_level": "medium",
    "requires_reboot": False,
    "notes": "Replace <nic1> and <nic2> with actual interface names (e.g., ens192, ens224). Use 'nmcli device status' to list available interfaces.",
}
```

### Step 5: Update the Modelfile
When adding patterns to local_commands.py, also add training examples to the Modelfile:

```
USER: configure network bonding with two interfaces
ASSISTANT: nmcli connection add type bond con-name bond0 ifname bond0 mode active-backup
nmcli connection add type ethernet con-name bond0-slave1 ifname <nic1> master bond0
nmcli connection add type ethernet con-name bond0-slave2 ifname <nic2> master bond0
nmcli connection up bond0
```

## RHEL Version Compatibility

### Commands that differ across versions

| Operation | RHEL 7 | RHEL 8/9 |
|-----------|--------|----------|
| Package install | `yum install` | `dnf install` |
| Firewall | `firewall-cmd` | `firewall-cmd` (same) |
| Network config | `ifcfg` scripts | `nmcli` preferred |
| Container runtime | `docker` | `podman` |
| Subscription | `subscription-manager` | `subscription-manager` (same) |
| Time sync | `ntpd` | `chronyd` |
| Init system | `systemd` (since 7) | `systemd` |

### Handling version differences in commands

```python
# Option 1: Use the modern command (RHEL 8/9) with notes
{
    "keywords": ["install", "package"],
    "commands": ["dnf install -y <package_name>"],
    "notes": "On RHEL 7, use 'yum' instead of 'dnf'. Both accept the same syntax.",
}

# Option 2: Provide both in notes
{
    "keywords": ["sync", "time", "ntp", "chrony"],
    "commands": [
        "systemctl enable --now chronyd",
        "chronyc sources -v",
    ],
    "notes": "RHEL 7 may use ntpd instead of chronyd. Check with 'rpm -q chrony'.",
}
```

## Keyword Matching Best Practices

### Good keyword sets
```python
# Specific and broad coverage
["disable", "selinux", "enforcing", "permissive"]
["create", "logical", "volume", "lvm", "lvcreate"]
["check", "disk", "space", "usage", "df", "storage"]
```

### Bad keyword sets
```python
# Too generic - will match too many queries
["set", "config"]
# Too specific - won't match natural language
["grubby-update-kernel-all-args"]
# Missing common synonyms
["hugepages"]  # Should also include "thp", "transparent"
```

## Quality Checklist

Before adding a new pattern:

- [ ] Keywords are all lowercase
- [ ] Keywords include common synonyms
- [ ] Description is clear and concise
- [ ] Commands are ordered correctly (dependencies first)
- [ ] Risk level matches the operation's impact
- [ ] `requires_reboot` is set correctly
- [ ] Notes explain placeholders (e.g., `<module_name>`)
- [ ] Commands work on RHEL 8/9 (note RHEL 7 differences)
- [ ] No duplicate descriptions in the database
- [ ] Corresponding Modelfile training example added
