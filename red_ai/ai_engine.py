import json
import urllib.request
from .system_info import get_system_info, format_system_context

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "red-ai-model"


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

    # Fall back to Ollama
    try:
        result = _call_ollama(prompt)
        result["source"] = "ollama"
        result = _detect_sysctl_in_response(result)
        return result
    except Exception:
        pass

    return {
        "error": (
            "No matching command found locally and Ollama is not available.\n"
            "\n"
            "To enable AI mode, set up the RED-AI custom model:\n"
            "  1. Install Ollama:  curl -fsSL https://ollama.ai/install.sh | sh\n"
            "  2. Build the model: ollama create red-ai-model -f Modelfile\n"
            "  3. Verify it works: ollama run red-ai-model \"check kernel version\"\n"
            "\n"
            "RED-AI uses its own fine-tuned Modelfile (based on Mistral) with 230+\n"
            "RHEL-specific training examples. No other models are needed.\n"
            "\n"
            "Or try rephrasing your request to match a local command pattern."
        ),
    }


def _call_ollama(prompt):
    """Call local Ollama LLM to generate commands.

    The SYSTEM prompt is already baked into the Modelfile, so we only send
    the system context and user request to avoid duplicate token processing.
    """
    system_info = get_system_info()
    system_context = format_system_context(system_info)

    full_prompt = "Current system information:\n{}\n\nUser request: {}".format(
        system_context, prompt)

    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": full_prompt,
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
