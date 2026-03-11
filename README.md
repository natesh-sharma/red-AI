# RED-AI - RHEL Configuration Tool

An intelligent command-line tool for RHEL Linux that simplifies system configuration using natural language prompts. Configure complex RHEL settings without memorizing command syntax.

**Developed by:** Natesh Sharma

## Features

- **Natural Language Interface**: Configure RHEL systems using plain English
- **AI-Powered**: Uses local Ollama LLM (Mistral) for intelligent command generation
- **Offline Fallback**: Built-in command database works without AI connectivity
- **Safety Features**:
  - Root privilege checking
  - Interactive confirmation prompts
  - Dry-run mode for testing
  - Risk level indicators (low / medium / high)
- **Execution Logging**: All commands logged to `/var/log/red-ai/executions.log`
- **Support For**:
  - Kernel configurations (transparent hugepages, sysctl, modules, SysRq)
  - kdump setup
  - SELinux management
  - Firewall configuration
  - Networking (nmcli, hostname)
  - Storage (disk usage, LVM, mounts)
  - Services (systemctl)
  - Users and password policies
  - Packages (yum/dnf)
  - Performance tuning (tuned profiles)
  - Time/NTP (chrony, timedatectl)
  - Logging (journalctl, rsyslog)
  - And more via AI mode...

## Prerequisites

- RHEL 7, 8, or 9
- Python 3.6+
- Direct root access (UID 0) for execution mode
- [Ollama](https://ollama.ai) (optional, for full AI mode)

## Installation

### Option 1: RPM Package (recommended for RHEL)

Build and install as a native RPM:
```bash
# Install build dependencies
sudo yum install -y rpm-build python3-devel python3-setuptools

# Build the RPM
./build_rpm.sh

# Install the RPM
sudo yum install -y ~/rpmbuild/RPMS/noarch/red-ai-*.rpm
```

### Option 2: pip install
```bash
pip3 install .
```

### Optional: Install Ollama for AI mode

```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull mistral
```

Without Ollama, RED-AI falls back to its built-in command database.

## Usage

### Basic Commands
```bash
# Show help
red-ai --help

# Show version
red-ai --version

# Show system information
red-ai --info

# Dry run to preview commands (no root required)
red-ai --dry-run "disable transparent hugepages"

# Execute a configuration (requires root)
red-ai "configure kdump"

# Skip confirmation prompts
red-ai -y "disable selinux"
```

### Examples
```bash
red-ai "check disk usage"
red-ai "open port 8080 in firewall"
red-ai "set timezone to America/New_York"
red-ai "list running services"
red-ai --dry-run "disable firewall"
```

## Options

| Option | Description |
|--------|-------------|
| `-h, --help` | Show help |
| `-d, --dry-run` | Preview without executing |
| `-y, --yes` | Skip confirmation |
| `-v, --version` | Show version |
| `-i, --info` | Show system information |

## Safety

- **Low Risk**: Information queries only
- **Medium Risk**: Standard configuration changes
- **High Risk**: Critical system modifications (SELinux, firewall disable, reboot)

Always test with `--dry-run` first!

## Uninstall

```bash
# If installed via RPM
sudo yum remove red-ai

# If installed via pip
pip3 uninstall red-ai
```
