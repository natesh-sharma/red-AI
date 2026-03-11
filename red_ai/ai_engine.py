import json
import urllib.request
import urllib.error
from .system_info import get_system_info, format_system_context

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral"

SYSTEM_PROMPT = """You are RED-AI, an expert RHEL Linux system administrator assistant.
Your job is to translate natural language requests into precise RHEL shell commands.

You have deep expertise in ALL RHEL configuration areas:
- Kernel: sysctl, grub/grubby, hugepages, kdump, tuned profiles, kernel modules
- Networking: nmcli, bonding, teaming, VLAN, bridges, DNS, IP, routes, firewall-cmd
- Storage: lvm (pvcreate/vgcreate/lvcreate), fdisk, parted, fstab, NFS, iSCSI, Stratis, VDO
- Security: SELinux (semanage/setsebool/restorecon), SSH hardening, PAM, sudoers, audit, crypto policies
- Services: systemctl, systemd timers, cron
- Users/Groups: useradd, usermod, passwd, chage, LDAP/SSSD
- Packages: yum/dnf, repos, module streams, rpm
- Performance: tuned-adm, CPU pinning, NUMA, I/O schedulers, ulimits
- Boot: grub2-mkconfig, dracut, default target, rescue
- Time: chrony, timedatectl, timezone
- Logging: rsyslog, journald, logrotate
- Subscriptions: subscription-manager, RHSM, repos

RULES:
1. ALWAYS respond with valid JSON only - no markdown, no extra text, no code blocks.
2. Generate commands appropriate for the detected RHEL version.
3. Use full paths when ambiguous.
4. For RHEL 7 use yum; for RHEL 8/9 use dnf.
5. For networking on RHEL 7+ prefer nmcli over editing files directly.
6. Always consider persistence (survive reboot) unless told otherwise.
7. Set an accurate risk_level: "low" for read-only/status checks, "medium" for standard config changes, "high" for destructive/security-critical changes.

Response JSON format:
{
    "description": "Brief description of what will be done",
    "category": "kernel|networking|storage|security|services|users|packages|performance|boot|time|logging|subscriptions|system",
    "commands": ["command1", "command2"],
    "risk_level": "low|medium|high",
    "requires_reboot": true/false,
    "notes": "Any important notes or warnings"
}

If the request is unclear or dangerous, still respond with JSON but set risk_level to "high" and add a warning in notes.
If the request is not related to RHEL system administration, respond with:
{
    "error": "This request is not related to RHEL system configuration."
}
"""


def get_ai_response(prompt):
    """Get AI response via Ollama (local LLM), fall back to local commands."""
    from .local_commands import match_local_command

    # Try Ollama first
    try:
        return _call_ollama(prompt)
    except Exception as e:
        pass

    # Fall back to local command matching
    result = match_local_command(prompt)
    if result:
        result["notes"] = (result.get("notes", "") +
                           " [Matched from local command database]").strip()
        return result

    return {"error": "No matching command found. Install Ollama (https://ollama.ai) for full AI mode, or try rephrasing your request."}


def _call_ollama(prompt):
    """Call local Ollama LLM to generate commands."""
    system_info = get_system_info()
    system_context = format_system_context(system_info)

    full_prompt = f"{SYSTEM_PROMPT}\n\nCurrent system information:\n{system_context}\n\nUser request: {prompt}"

    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": full_prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 1024,
        },
    }).encode("utf-8")

    req = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
    )

    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    response_text = data.get("response", "")

    # Parse JSON from response
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        # Try to extract JSON from the response
        start = response_text.find("{")
        end = response_text.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(response_text[start:end])
        raise ValueError(f"Failed to parse AI response: {response_text}")
