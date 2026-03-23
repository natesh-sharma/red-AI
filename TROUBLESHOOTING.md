# Troubleshooting

## Common Issues

### "No matching command found"

**Cause:** The prompt didn't match any local command pattern and Ollama is unavailable.

**Fix:**
1. Try rephrasing your request with common RHEL terms
2. Set up Ollama with the custom model (see below)
3. Check `red-ai --dry-run "your request"` for matches

### Ollama Connection Refused

**Cause:** Ollama service is not running.

**Fix:**
```bash
systemctl start ollama
systemctl enable ollama    # auto-start on boot
curl http://localhost:11434/api/tags   # verify it's up
```

### "Model not found" Error

**Cause:** The `red-ai-model` hasn't been created from the Modelfile.

**Fix:**
```bash
cd /opt/red-ai    # or wherever RED-AI is installed
ollama create red-ai-model -f Modelfile
ollama list       # verify red-ai-model appears
```

### "Must be run as root"

**Cause:** Execution mode requires root privileges.

**Fix:**
```bash
# Use dry-run to preview without root
red-ai --dry-run "your request"

# Or run as root for execution
sudo red-ai "your request"
```

### Slow Ollama Responses

**Cause:** First request loads the model into memory (~4GB for Mistral).

**Fix:**
- First request takes 10-30s (model loading). Subsequent requests are faster.
- Ensure 4GB+ free RAM: `free -h`
- Keep Ollama running to avoid cold starts

### Permission Denied on Log Files

**Cause:** `/var/log/red-ai/` directory doesn't exist or has wrong permissions.

**Fix:**
```bash
sudo mkdir -p /var/log/red-ai
sudo chmod 750 /var/log/red-ai
```

### RPM Build Fails

**Cause:** Missing build dependencies.

**Fix:**
```bash
yum install -y rpm-build python3-setuptools
./build_rpm.sh
```

### Tests Fail After Changes

**Fix:**
```bash
# Run the full validation suite
./scripts/validate.sh

# Or run tests directly
python3 -m unittest discover -s tests -v
```

## RHEL Version-Specific Issues

| Issue | RHEL 7 | RHEL 8 | RHEL 9 |
|-------|--------|--------|--------|
| Python version | 3.6 (SCL) | 3.6+ | 3.9+ |
| Package manager | `yum` | `yum`/`dnf` | `dnf` |
| crashkernel | `auto` | `auto` | Range syntax |
| NTP service | `ntpd` | `chronyd` | `chronyd` |
| Firewall | `iptables`/`firewalld` | `firewalld` | `firewalld` |

## Getting Help

1. Run `red-ai --info` to check system details
2. Run `red-ai --history` to review past executions
3. Check logs: `ls /var/log/red-ai/`
4. Open an issue on GitHub with `--info` output and the failing command
