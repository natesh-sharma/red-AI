import json
import os
import subprocess
import time
import urllib.request
from .system_info import get_system_info, format_system_context

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2:1.5b"


def _is_ollama_running():
    """Check if Ollama is responding on its API port."""
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags")
        with urllib.request.urlopen(req, timeout=3):
            return True
    except Exception:
        return False


def _start_ollama():
    """Try to start Ollama if installed but not running.

    Attempts systemctl first (Linux service), then 'ollama serve' as
    a background process. Returns True if Ollama becomes available.
    """
    # Check if ollama binary exists
    ollama_bin = None
    for path in ["/usr/local/bin/ollama", "/usr/bin/ollama"]:
        if os.path.isfile(path):
            ollama_bin = path
            break
    if ollama_bin is None:
        return False

    # Try systemctl first (works on RHEL with ollama.service)
    try:
        subprocess.run(
            ["systemctl", "start", "ollama"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=10,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        # systemctl not available or failed, try direct serve
        try:
            subprocess.Popen(
                [ollama_bin, "serve"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
        except OSError:
            return False

    # Wait for Ollama to become ready (up to 10 seconds)
    for _ in range(10):
        time.sleep(1)
        if _is_ollama_running():
            return True
    return False


def _detect_sysctl_in_response(result):
    """Detect sysctl commands in AI response and add persist_mode flag.

    If the response contains 'sysctl -w param=value', extract the param
    and value so the CLI can prompt the user for persistence choice.
    """
    import re

    commands = result.get("commands", [])
    if not commands:
        return result

    # Look for sysctl -w param=value in commands
    for cmd in commands:
        match = re.match(r'^sysctl\s+-w\s+([\w.:-]+)=(.+)$', cmd.strip())
        if match:
            param = match.group(1)
            value = match.group(2)
            namespace = param.split(".")[0]
            conf_file = "/etc/sysctl.d/99-{}.conf".format(namespace)

            result["persist_mode"] = "ask"
            result["sysctl_param"] = param
            result["sysctl_value"] = value
            result["sysctl_conf"] = conf_file
            # Only keep the sysctl -w command; CLI will build the rest
            result["commands"] = [cmd.strip()]
            return result

    return result


def get_ai_response(prompt):
    """Get AI response via local commands first, fall back to Ollama (local LLM)."""
    from .local_commands import match_local_command

    # Try local command matching first (instant)
    result = match_local_command(prompt)
    if result:
        result["source"] = "local_commands"
        result["notes"] = (result.get("notes", "") +
                           " [Matched from local command database]").strip()
        return result

    # Fall back to Ollama (auto-start if installed but not running)
    if not _is_ollama_running():
        from .executor import color
        print(color("Ollama not running. Attempting to start...", "yellow"))
        if _start_ollama():
            print(color("Ollama started successfully.", "green"))
        else:
            return {
                "error": (
                    "No matching command found locally and Ollama could not be started.\n"
                    "\n"
                    "To enable AI mode:\n"
                    "  1. Install Ollama:  curl -fsSL https://ollama.ai/install.sh | sh\n"
                    "  2. Pull the model:  ollama pull qwen2:1.5b\n"
                    "  3. Start Ollama:    systemctl start ollama\n"
                    "\n"
                    "Or try rephrasing your request to match a local command pattern."
                ),
            }

    try:
        result = _call_ollama(prompt)
        result["source"] = "ollama"
        result = _detect_sysctl_in_response(result)
        return result
    except Exception:
        pass

    return {
        "error": (
            "No matching command found locally and Ollama query failed.\n"
            "\n"
            "Verify Ollama is working:\n"
            "  1. Check status:  systemctl status ollama\n"
            "  2. Pull model:    ollama pull qwen2:1.5b\n"
            "  3. Test it:       ollama run qwen2:1.5b \"hello\"\n"
            "\n"
            "Or try rephrasing your request to match a local command pattern."
        ),
    }


SYSTEM_PROMPT = (
    "You are RED-AI, an expert RHEL Linux system administrator assistant. "
    "Translate natural language requests into precise RHEL shell commands. "
    "ALWAYS respond with valid JSON only - no markdown, no extra text. "
    "Response format: "
    '{"description":"Brief description","category":"kernel|networking|storage|security|services|users|packages|performance|boot|time|logging|subscriptions|system",'
    '"commands":["cmd1","cmd2"],"risk_level":"low|medium|high","requires_reboot":true/false,"notes":"warnings"} '
    "Rules: Use full paths when ambiguous. For RHEL 7 use yum; RHEL 8/9 use dnf. "
    "Prefer nmcli for networking. Set accurate risk_level. "
    "For sysctl changes, ONLY use 'sysctl -w param=value' - the tool handles persistence. "
    "If the request is not RHEL-related, respond with: {\"error\":\"Not related to RHEL system configuration.\"}"
)


def _call_ollama(prompt):
    """Call local Ollama LLM to generate commands.

    Sends a system prompt with RHEL expertise context and the user request.
    """
    system_info = get_system_info()
    system_context = format_system_context(system_info)

    full_prompt = "Current system information:\n{}\n\nUser request: {}".format(
        system_context, prompt)

    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": full_prompt,
        "system": SYSTEM_PROMPT,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 256,
        },
    }).encode("utf-8")

    req = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
    )

    with urllib.request.urlopen(req, timeout=30) as resp:
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
