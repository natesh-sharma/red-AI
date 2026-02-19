# RED-AI - RHEL Configuration Tool

An intelligent command-line tool for RHEL Linux that simplifies system configuration using natural language prompts. Configure complex RHEL settings without memorizing command syntax.

**Developed by:** Natesh Sharma

## Features

- **Natural Language Interface**: Configure RHEL systems using plain English
- **Comprehensive Command Database**: Queries Supabase for pre-configured commands
- **Safety Features**:
  - Root privilege checking
  - Interactive confirmation prompts
  - Dry-run mode for testing
  - Risk level indicators
- **Execution Logging**: All commands logged to database
- **Support For**:
  - Kernel configurations (transparent hugepages, etc.)
  - kdump setup
  - SELinux management
  - Firewall configuration
  - And more...

## Prerequisites

- RHEL 7, 8, or 9
- gcc and make
- Direct root access (UID 0)
- Internet connection (for Supabase)

## Installation

### 1. Install Dependencies
```bash
# RHEL 7/8
sudo yum install -y gcc make

# RHEL 9
sudo dnf install -y gcc make
```

### 2. Build the Tool
```bash
make
```

### 3. Set Environment Variables
```bash
export SUPABASE_URL="your_project_url"
export SUPABASE_SERVICE_ROLE_KEY="your_service_role_key"
```

## Usage

**Important:** RED-AI must be run as root directly (UID 0). It will NOT work with `sudo` or when executed by non-root users.

### Basic Commands
```bash
# As root user:

# Check help
./red-ai --help

# Dry run to preview commands
./red-ai --dry-run "disable transparent hugepages"

# Execute a configuration
./red-ai "configure kdump"

# Skip confirmation prompts
./red-ai -y "disable selinux"
```

## Pre-Configured Commands

The tool includes commands for:
- Disable/enable transparent hugepages
- Configure/disable kdump
- Manage SELinux
- Control firewall
- Check system status

## Adding Custom Commands

Insert commands into Supabase:
```sql
INSERT INTO command_definitions (
    category, action, keywords, description,
    commands, requires_reboot, risk_level
) VALUES (
    'kernel',
    'configure',
    ARRAY['disable', 'transparent', 'hugepages'],
    'Disable transparent hugepages',
    '["grubby --update-kernel=ALL --args=\"transparent_hugepage=never\""]'::jsonb,
    true,
    'medium'
);
```

## Database Setup

The tool requires a Supabase database with these tables:
- `command_definitions` - Command mappings and metadata
- `execution_history` - Audit log of executions
- `system_configurations` - Current system state

See QUICK_START.md for database migration details.

## Options

| Option | Description |
|--------|-------------|
| `-h, --help` | Show help |
| `-d, --dry-run` | Preview without executing |
| `-y, --yes` | Skip confirmation |
| `-v, --version` | Show version |

## Safety

- **Low Risk**: Information queries only
- **Medium Risk**: Standard configuration changes
- **High Risk**: Critical system modifications

Always test with `--dry-run` first!

## Uninstall

```bash
make clean
```

## License

MIT
