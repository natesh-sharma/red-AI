# RED-AI Quick Start Guide

## 5-Minute Setup

### 1. Build the Tool
```bash
make
./red-ai --help
```

### 2. Configure Supabase (Optional)
```bash
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="your_service_key"
```

### 3. Try It Out
**Must run as root directly (not with sudo):**
```bash
# Dry run - see what would execute
./red-ai --dry-run "check kdump status"

# Execute
./red-ai "configure kdump"
```

## Database Setup

Create tables in Supabase:

```sql
CREATE TABLE command_definitions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  category text NOT NULL,
  action text NOT NULL,
  keywords text[] NOT NULL,
  description text NOT NULL,
  commands jsonb NOT NULL,
  requires_reboot boolean DEFAULT false,
  risk_level text DEFAULT 'medium'
);

CREATE TABLE execution_history (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  command_def_id uuid REFERENCES command_definitions(id),
  user_prompt text NOT NULL,
  matched_intent text NOT NULL,
  commands_executed jsonb NOT NULL,
  status text NOT NULL,
  output text,
  executed_at timestamptz DEFAULT now()
);

CREATE TABLE system_configurations (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  config_key text UNIQUE NOT NULL,
  config_value jsonb NOT NULL,
  is_active boolean DEFAULT true,
  last_modified timestamptz DEFAULT now()
);
```

## Sample Commands to Add

### Disable Transparent Hugepages
```sql
INSERT INTO command_definitions (
    category, action, keywords, description,
    commands, requires_reboot, risk_level
) VALUES (
    'kernel', 'configure',
    ARRAY['disable', 'transparent', 'hugepages', 'thp'],
    'Disable transparent hugepages',
    '["grubby --update-kernel=ALL --args=\"transparent_hugepage=never\"", "grub2-mkconfig -o /boot/grub2/grub.cfg"]'::jsonb,
    true, 'medium'
);
```

### Configure kdump
```sql
INSERT INTO command_definitions (
    category, action, keywords, description,
    commands, requires_reboot, risk_level
) VALUES (
    'kdump', 'configure',
    ARRAY['configure', 'kdump', 'crash', 'dump'],
    'Configure kdump utility',
    '["yum install -y kexec-tools", "systemctl enable kdump", "kdumpctl start"]'::jsonb,
    false, 'low'
);
```

### Check Kdump Status
```sql
INSERT INTO command_definitions (
    category, action, keywords, description,
    commands, requires_reboot, risk_level
) VALUES (
    'kdump', 'info',
    ARRAY['check', 'kdump', 'status'],
    'Check kdump status',
    '["systemctl status kdump", "kdumpctl showmem"]'::jsonb,
    false, 'low'
);
```

## Common Usage Patterns

**Run as root directly (not with sudo):**
```bash
# Preview before execution
./red-ai --dry-run "your command"

# Execute with automatic confirmation
./red-ai -y "your command"

# Full interactive mode
./red-ai "your command"
```

## Troubleshooting

### "RED-AI must be run as root (UID 0) only"
- You must run this tool as root directly
- Using `sudo` will NOT work
- Log in as root user and try again
- Check your UID is 0: `id`

### "No matching configuration found"
- Add the command to your Supabase database
- Check command keywords match your prompt

### Build errors
- Ensure gcc and make are installed
- Check CFLAGS in Makefile for your OS

## Next Steps

1. Build and test the tool
2. Set up Supabase database
3. Add custom command definitions
4. Integrate into your system administration workflow

## Features Roadmap

- AI-powered prompt matching
- Command suggestions
- Batch execution
- Rollback capabilities
- Configuration backup/restore
