"""Built-in local command definitions for offline/fallback mode."""

LOCAL_COMMANDS = [
    # Kernel
    {
        "keywords": ["disable", "transparent", "hugepages", "thp"],
        "description": "Disable transparent hugepages (runtime + persistent via grub)",
        "category": "kernel",
        "commands": [
            "echo never > /sys/kernel/mm/transparent_hugepage/enabled",
            "echo never > /sys/kernel/mm/transparent_hugepage/defrag",
            "grubby --update-kernel=ALL --args='transparent_hugepage=never'",
        ],
        "risk_level": "medium",
        "requires_reboot": False,
        "notes": "Runtime change is immediate. Grub change persists across reboots.",
    },
    {
        "keywords": ["enable", "transparent", "hugepages", "thp"],
        "description": "Enable transparent hugepages",
        "category": "kernel",
        "commands": [
            "echo always > /sys/kernel/mm/transparent_hugepage/enabled",
            "grubby --update-kernel=ALL --remove-args='transparent_hugepage=never'",
        ],
        "risk_level": "medium",
        "requires_reboot": False,
        "notes": "Runtime change is immediate. Grub change persists across reboots.",
    },
    {
        "keywords": ["load", "kernel", "module"],
        "description": "Load a kernel module",
        "category": "kernel",
        "commands": ["modprobe <module_name>"],
        "risk_level": "medium",
        "requires_reboot": False,
        "notes": "Replace <module_name> with the actual module. Use 'lsmod' to list loaded modules.",
    },
    {
        "keywords": ["unload", "remove", "kernel", "module"],
        "description": "Unload a kernel module",
        "category": "kernel",
        "commands": ["modprobe -r <module_name>"],
        "risk_level": "medium",
        "requires_reboot": False,
        "notes": "Replace <module_name> with the actual module.",
    },
    {
        "keywords": ["list", "kernel", "modules", "loaded"],
        "description": "List loaded kernel modules",
        "category": "kernel",
        "commands": ["lsmod"],
        "risk_level": "low",
        "requires_reboot": False,
        "notes": "",
    },
    {
        "keywords": ["sysctl", "kernel", "parameters"],
        "description": "Show all sysctl kernel parameters",
        "category": "kernel",
        "commands": ["sysctl -a"],
        "risk_level": "low",
        "requires_reboot": False,
        "notes": "",
    },
    {
        "keywords": ["enable", "sysrq"],
        "description": "Enable SysRq key (runtime + persistent)",
        "category": "kernel",
        "commands": [
            "sysctl -w kernel.sysrq=1",
            "echo 'kernel.sysrq = 1' >> /etc/sysctl.d/99-sysrq.conf",
        ],
        "risk_level": "medium",
        "requires_reboot": False,
        "notes": "Enables all SysRq functions. Use a bitmask value (e.g. 176) to enable only specific functions.",
    },
    {
        "keywords": ["disable", "sysrq"],
        "description": "Disable SysRq key (runtime + persistent)",
        "category": "kernel",
        "commands": [
            "sysctl -w kernel.sysrq=0",
            "echo 'kernel.sysrq = 0' >> /etc/sysctl.d/99-sysrq.conf",
        ],
        "risk_level": "medium",
        "requires_reboot": False,
        "notes": "",
    },
    {
        "keywords": ["check", "sysrq", "status"],
        "description": "Check current SysRq setting",
        "category": "kernel",
        "commands": ["sysctl kernel.sysrq"],
        "risk_level": "low",
        "requires_reboot": False,
        "notes": "",
    },
    # Kdump
    {
        "keywords": ["configure", "kdump", "setup"],
        "description": "Configure and enable kdump crash recovery",
        "category": "kernel",
        "commands": [
            "yum install -y kexec-tools",
            "systemctl enable kdump",
            "systemctl start kdump",
        ],
        "risk_level": "medium",
        "requires_reboot": False,
        "notes": "Kdump requires reserved memory. Check /etc/kdump.conf for settings.",
    },
    {
        "keywords": ["disable", "kdump"],
        "description": "Disable kdump crash recovery",
        "category": "kernel",
        "commands": [
            "systemctl stop kdump",
            "systemctl disable kdump",
        ],
        "risk_level": "medium",
        "requires_reboot": False,
        "notes": "",
    },
    {
        "keywords": ["check", "status", "kdump"],
        "description": "Check kdump status",
        "category": "kernel",
        "commands": [
            "systemctl status kdump",
            "kdumpctl status",
        ],
        "risk_level": "low",
        "requires_reboot": False,
        "notes": "",
    },
    # SELinux
    {
        "keywords": ["disable", "selinux"],
        "description": "Disable SELinux (requires reboot for full effect)",
        "category": "security",
        "commands": [
            "setenforce 0",
            "sed -i 's/^SELINUX=.*/SELINUX=disabled/' /etc/selinux/config",
        ],
        "risk_level": "high",
        "requires_reboot": True,
        "notes": "WARNING: Disabling SELinux reduces system security. Reboot required for permanent change.",
    },
    {
        "keywords": ["enable", "selinux"],
        "description": "Enable SELinux in enforcing mode",
        "category": "security",
        "commands": [
            "sed -i 's/^SELINUX=.*/SELINUX=enforcing/' /etc/selinux/config",
        ],
        "risk_level": "high",
        "requires_reboot": True,
        "notes": "Reboot required. Run 'fixfiles -F onboot' if re-enabling after being disabled.",
    },
    {
        "keywords": ["check", "status", "selinux"],
        "description": "Check SELinux status",
        "category": "security",
        "commands": ["getenforce", "sestatus"],
        "risk_level": "low",
        "requires_reboot": False,
        "notes": "",
    },
    {
        "keywords": ["permissive", "selinux"],
        "description": "Set SELinux to permissive mode",
        "category": "security",
        "commands": [
            "setenforce 0",
            "sed -i 's/^SELINUX=.*/SELINUX=permissive/' /etc/selinux/config",
        ],
        "risk_level": "medium",
        "requires_reboot": False,
        "notes": "Permissive mode logs violations but does not enforce. Persistent via config.",
    },
    # Firewall
    {
        "keywords": ["disable", "firewall", "firewalld"],
        "description": "Disable firewalld",
        "category": "security",
        "commands": [
            "systemctl stop firewalld",
            "systemctl disable firewalld",
        ],
        "risk_level": "high",
        "requires_reboot": False,
        "notes": "WARNING: Disabling the firewall exposes all ports.",
    },
    {
        "keywords": ["enable", "firewall", "firewalld"],
        "description": "Enable firewalld",
        "category": "security",
        "commands": [
            "systemctl enable firewalld",
            "systemctl start firewalld",
        ],
        "risk_level": "medium",
        "requires_reboot": False,
        "notes": "",
    },
    {
        "keywords": ["check", "status", "firewall", "firewalld"],
        "description": "Check firewall status and rules",
        "category": "security",
        "commands": [
            "systemctl status firewalld",
            "firewall-cmd --list-all",
        ],
        "risk_level": "low",
        "requires_reboot": False,
        "notes": "",
    },
    {
        "keywords": ["add", "open", "port", "firewall"],
        "description": "Open a port in firewalld",
        "category": "security",
        "commands": [
            "firewall-cmd --permanent --add-port=<port>/tcp",
            "firewall-cmd --reload",
        ],
        "risk_level": "medium",
        "requires_reboot": False,
        "notes": "Replace <port> with the port number. Add --zone=<zone> if not using default zone.",
    },
    {
        "keywords": ["remove", "close", "port", "firewall"],
        "description": "Close a port in firewalld",
        "category": "security",
        "commands": [
            "firewall-cmd --permanent --remove-port=<port>/tcp",
            "firewall-cmd --reload",
        ],
        "risk_level": "medium",
        "requires_reboot": False,
        "notes": "Replace <port> with the port number.",
    },
    # Networking
    {
        "keywords": ["check", "network", "interfaces", "connections"],
        "description": "Check network interfaces and connections",
        "category": "networking",
        "commands": [
            "nmcli device status",
            "nmcli connection show",
            "ip addr show",
        ],
        "risk_level": "low",
        "requires_reboot": False,
        "notes": "",
    },
    {
        "keywords": ["restart", "network", "networkmanager"],
        "description": "Restart NetworkManager",
        "category": "networking",
        "commands": ["systemctl restart NetworkManager"],
        "risk_level": "medium",
        "requires_reboot": False,
        "notes": "This may briefly interrupt network connectivity.",
    },
    {
        "keywords": ["set", "hostname"],
        "description": "Set system hostname",
        "category": "networking",
        "commands": ["hostnamectl set-hostname <new-hostname>"],
        "risk_level": "low",
        "requires_reboot": False,
        "notes": "Replace <new-hostname> with the desired hostname.",
    },
    {
        "keywords": ["check", "hostname"],
        "description": "Check current hostname",
        "category": "networking",
        "commands": ["hostnamectl"],
        "risk_level": "low",
        "requires_reboot": False,
        "notes": "",
    },
    # Storage
    {
        "keywords": ["check", "disk", "usage", "space"],
        "description": "Check disk usage",
        "category": "storage",
        "commands": ["df -hT", "du -sh /* 2>/dev/null | sort -rh | head -10"],
        "risk_level": "low",
        "requires_reboot": False,
        "notes": "",
    },
    {
        "keywords": ["list", "lvm", "volumes", "logical"],
        "description": "List LVM volumes and groups",
        "category": "storage",
        "commands": ["pvs", "vgs", "lvs"],
        "risk_level": "low",
        "requires_reboot": False,
        "notes": "",
    },
    {
        "keywords": ["check", "mounts", "fstab", "mounted"],
        "description": "Check mounted filesystems",
        "category": "storage",
        "commands": ["mount | column -t", "cat /etc/fstab"],
        "risk_level": "low",
        "requires_reboot": False,
        "notes": "",
    },
    # Services
    {
        "keywords": ["list", "services", "running"],
        "description": "List all running services",
        "category": "services",
        "commands": ["systemctl list-units --type=service --state=running"],
        "risk_level": "low",
        "requires_reboot": False,
        "notes": "",
    },
    {
        "keywords": ["list", "services", "enabled"],
        "description": "List all enabled services",
        "category": "services",
        "commands": ["systemctl list-unit-files --type=service --state=enabled"],
        "risk_level": "low",
        "requires_reboot": False,
        "notes": "",
    },
    {
        "keywords": ["enable", "service"],
        "description": "Enable and start a service",
        "category": "services",
        "commands": [
            "systemctl enable <service_name>",
            "systemctl start <service_name>",
        ],
        "risk_level": "medium",
        "requires_reboot": False,
        "notes": "Replace <service_name> with the actual service name.",
    },
    {
        "keywords": ["disable", "service"],
        "description": "Disable and stop a service",
        "category": "services",
        "commands": [
            "systemctl stop <service_name>",
            "systemctl disable <service_name>",
        ],
        "risk_level": "medium",
        "requires_reboot": False,
        "notes": "Replace <service_name> with the actual service name.",
    },
    {
        "keywords": ["restart", "service"],
        "description": "Restart a service",
        "category": "services",
        "commands": ["systemctl restart <service_name>"],
        "risk_level": "medium",
        "requires_reboot": False,
        "notes": "Replace <service_name> with the actual service name.",
    },
    # Users
    {
        "keywords": ["list", "users"],
        "description": "List system users",
        "category": "users",
        "commands": [
            "cat /etc/passwd",
            "awk -F: '$3 >= 1000 {print $1}' /etc/passwd",
        ],
        "risk_level": "low",
        "requires_reboot": False,
        "notes": "Second command shows only regular (non-system) users.",
    },
    {
        "keywords": ["check", "password", "policy", "aging"],
        "description": "Check password aging policy",
        "category": "users",
        "commands": [
            "cat /etc/login.defs | grep -E '^PASS_'",
            "chage -l <username>",
        ],
        "risk_level": "low",
        "requires_reboot": False,
        "notes": "Replace <username> with the actual username.",
    },
    # Packages
    {
        "keywords": ["check", "updates", "available"],
        "description": "Check for available package updates",
        "category": "packages",
        "commands": ["yum check-update || true"],
        "risk_level": "low",
        "requires_reboot": False,
        "notes": "Use 'dnf check-update' on RHEL 8+.",
    },
    {
        "keywords": ["list", "installed", "packages"],
        "description": "List installed packages",
        "category": "packages",
        "commands": ["rpm -qa --last | head -20"],
        "risk_level": "low",
        "requires_reboot": False,
        "notes": "Shows 20 most recently installed packages.",
    },
    # Performance / Tuned
    {
        "keywords": ["check", "tuned", "profile"],
        "description": "Check current tuned profile",
        "category": "performance",
        "commands": [
            "tuned-adm active",
            "tuned-adm list",
        ],
        "risk_level": "low",
        "requires_reboot": False,
        "notes": "",
    },
    {
        "keywords": ["set", "tuned", "profile"],
        "description": "Set a tuned performance profile",
        "category": "performance",
        "commands": ["tuned-adm profile <profile_name>"],
        "risk_level": "medium",
        "requires_reboot": False,
        "notes": "Replace <profile_name> with the desired profile (e.g. throughput-performance, latency-performance).",
    },
    # System
    {
        "keywords": ["check", "system", "status", "overview"],
        "description": "Show system status overview",
        "category": "system",
        "commands": [
            "hostnamectl",
            "uptime",
            "free -h",
            "df -hT /",
        ],
        "risk_level": "low",
        "requires_reboot": False,
        "notes": "",
    },
    {
        "keywords": ["check", "uptime"],
        "description": "Check system uptime",
        "category": "system",
        "commands": ["uptime"],
        "risk_level": "low",
        "requires_reboot": False,
        "notes": "",
    },
    {
        "keywords": ["check", "memory", "ram"],
        "description": "Check memory usage",
        "category": "system",
        "commands": ["free -h", "cat /proc/meminfo | head -5"],
        "risk_level": "low",
        "requires_reboot": False,
        "notes": "",
    },
    {
        "keywords": ["reboot", "system", "restart"],
        "description": "Reboot the system",
        "category": "system",
        "commands": ["systemctl reboot"],
        "risk_level": "high",
        "requires_reboot": True,
        "notes": "WARNING: This will immediately reboot the system.",
    },
    # Time
    {
        "keywords": ["check", "timezone", "time"],
        "description": "Check current timezone and time settings",
        "category": "time",
        "commands": ["timedatectl"],
        "risk_level": "low",
        "requires_reboot": False,
        "notes": "",
    },
    {
        "keywords": ["set", "timezone"],
        "description": "Set system timezone",
        "category": "time",
        "commands": ["timedatectl set-timezone <timezone>"],
        "risk_level": "low",
        "requires_reboot": False,
        "notes": "Replace <timezone> with the desired timezone (e.g. America/New_York). List available with 'timedatectl list-timezones'.",
    },
    {
        "keywords": ["check", "chrony", "ntp", "time", "sync"],
        "description": "Check chrony/NTP time synchronization",
        "category": "time",
        "commands": [
            "chronyc tracking",
            "chronyc sources -v",
        ],
        "risk_level": "low",
        "requires_reboot": False,
        "notes": "",
    },
    # Logging
    {
        "keywords": ["check", "journal", "logs", "journalctl"],
        "description": "Check recent system journal logs",
        "category": "logging",
        "commands": ["journalctl -xe --no-pager | tail -50"],
        "risk_level": "low",
        "requires_reboot": False,
        "notes": "",
    },
    {
        "keywords": ["check", "rsyslog", "syslog"],
        "description": "Check rsyslog configuration and status",
        "category": "logging",
        "commands": [
            "systemctl status rsyslog",
            "cat /etc/rsyslog.conf",
        ],
        "risk_level": "low",
        "requires_reboot": False,
        "notes": "",
    },
]


def match_local_command(prompt):
    """Match a user prompt against local command definitions using keyword scoring.

    Uses a ratio-based scoring: what fraction of the entry's keywords appear
    in the prompt. This prevents entries with few generic keywords from
    winning over more specific matches.

    Returns the best matching command definition as a dict matching the AI
    response JSON format, or None if no good match is found.
    """
    prompt_lower = prompt.lower()
    prompt_words = set(prompt_lower.split())

    best_match = None
    best_score = 0.0
    best_hits = 0

    for cmd in LOCAL_COMMANDS:
        keywords = cmd["keywords"]
        hits = 0
        for keyword in keywords:
            if keyword in prompt_words:
                hits += 2  # exact word match
            elif keyword in prompt_lower:
                hits += 1  # substring match

        if hits == 0:
            continue

        # Score = fraction of keywords matched (weighted hits / max possible)
        max_possible = len(keywords) * 2
        score = hits / max_possible

        if score > best_score or (score == best_score and hits > best_hits):
            best_score = score
            best_match = cmd
            best_hits = hits

    # Require at least 40% keyword coverage and at least 2 raw hits
    if best_score < 0.4 or best_hits < 2:
        return None

    return {
        "description": best_match["description"],
        "category": best_match["category"],
        "commands": list(best_match["commands"]),
        "risk_level": best_match["risk_level"],
        "requires_reboot": best_match["requires_reboot"],
        "notes": best_match.get("notes", ""),
    }
