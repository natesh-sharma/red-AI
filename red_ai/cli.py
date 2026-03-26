#!/usr/bin/env python3
import argparse
import os
import sys

from . import __version__
from .ai_engine import get_ai_response
from .executor import execute_commands, color, prompt_choice
from .logger import log_execution, read_history
from .system_info import get_system_info, format_system_context, get_rhel_major_version


def get_response(prompt):
    """Get AI response for the prompt."""
    return get_ai_response(prompt)


def _handle_kdump_enable(dry_run):
    """Verify kdump prerequisites before enabling.

    Checks crashkernel boot param, kexec-tools package, and current
    kdump status. Returns a response dict with the appropriate commands,
    or None if the user aborts.
    """
    import subprocess

    print(color("\nRunning kdump preflight checks...", "blue"))
    checks = []
    commands = []
    needs_reboot = False

    # Check 1: crashkernel boot parameter
    try:
        with open("/proc/cmdline") as f:
            cmdline = f.read()
        has_crashkernel = "crashkernel=" in cmdline
    except (IOError, OSError):
        has_crashkernel = False

    if has_crashkernel:
        checks.append(("crashkernel boot parameter", True, "configured"))
    else:
        checks.append(("crashkernel boot parameter", False, "NOT configured"))
        rhel_major = get_rhel_major_version()
        if rhel_major is not None and rhel_major >= 9:
            crashkernel_val = "1G-4G:192M,4G-64G:256M,64G-:512M"
        else:
            crashkernel_val = "auto"
        commands.append("grubby --update-kernel=ALL --args='crashkernel={}'".format(crashkernel_val))
        needs_reboot = True

    # Check 2: kexec-tools installed
    try:
        result = subprocess.run(
            ["rpm", "-q", "kexec-tools"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True, timeout=5,
        )
        has_kexec = result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        has_kexec = False

    if has_kexec:
        checks.append(("kexec-tools package", True, "installed"))
    else:
        checks.append(("kexec-tools package", False, "NOT installed"))
        commands.append("yum install -y kexec-tools")

    # Check 3: kdump service status
    try:
        result = subprocess.run(
            ["systemctl", "is-active", "kdump"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True, timeout=5,
        )
        kdump_active = result.stdout.strip() == "active"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        kdump_active = False

    try:
        result = subprocess.run(
            ["systemctl", "is-enabled", "kdump"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True, timeout=5,
        )
        kdump_enabled = result.stdout.strip() == "enabled"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        kdump_enabled = False

    if kdump_active and kdump_enabled:
        checks.append(("kdump service", True, "active and enabled"))
    else:
        status_parts = []
        if not kdump_enabled:
            status_parts.append("not enabled")
            commands.append("systemctl enable kdump")
        if not kdump_active:
            status_parts.append("not active")
            commands.append("systemctl start kdump")
        checks.append(("kdump service", False, ", ".join(status_parts)))

    # Display preflight results
    print(color("\nPreflight Check Results:", "blue"))
    for name, passed, detail in checks:
        icon = color("[PASS]", "green") if passed else color("[FAIL]", "red")
        print("  {} {} - {}".format(icon, name, detail))

    if not commands:
        print(color("\nkdump is already properly configured and running.", "green"))
        return {"commands": [], "description": "kdump already configured"}

    if needs_reboot:
        print(color("\nWARNING: crashkernel parameter requires a reboot to take effect.", "yellow"))

    if dry_run:
        return {
            "description": "Configure and enable kdump crash recovery",
            "category": "kernel",
            "commands": commands,
            "risk_level": "medium",
            "requires_reboot": needs_reboot,
            "notes": "Reboot required for crashkernel." if needs_reboot else "",
            "source": "local_commands",
        }

    from .executor import confirm
    if not confirm("\nProceed with kdump configuration?"):
        print(color("Aborted.", "yellow"))
        return None

    return {
        "description": "Configure and enable kdump crash recovery",
        "category": "kernel",
        "commands": commands,
        "risk_level": "medium",
        "requires_reboot": needs_reboot,
        "notes": "Reboot required for crashkernel." if needs_reboot else "",
        "source": "local_commands",
    }


def main():
    parser = argparse.ArgumentParser(
        prog="red-ai",
        description=(
            "AI-powered RHEL system configuration tool. "
            "Describe tasks in plain English and red-ai generates, "
            "previews, and optionally executes the appropriate commands. "
            "Uses a local database of 230+ RHEL patterns with Ollama AI fallback."
        ),
        epilog=(
            "examples:\n"
            "  red-ai --dry-run disable transparent hugepages\n"
            "  red-ai enable kdump\n"
            "  red-ai set vm.swappiness to 10\n"
            "  red-ai --info\n"
            "  red-ai --history 5\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "prompt", nargs="*",
        help="natural language description of the configuration task "
             "(e.g., 'disable SELinux', 'enable ip forwarding')")
    parser.add_argument(
        "-d", "--dry-run", action="store_true",
        help="preview generated commands without executing; "
             "does not require root privileges")
    parser.add_argument(
        "-y", "--yes", action="store_true",
        help="skip confirmation prompts and execute immediately; "
             "use with caution for high-risk operations")
    parser.add_argument(
        "-v", "--version", action="store_true",
        help="show the red-ai version number and exit")
    parser.add_argument(
        "-i", "--info", action="store_true",
        help="display detected system information (RHEL version, "
             "kernel, SELinux, firewalld status)")
    parser.add_argument(
        "--history", nargs="?", const=10, type=int, metavar="N",
        help="show the last N command executions from the audit log "
             "(default: 10)")

    args = parser.parse_args()

    if args.version:
        print(f"red-ai {__version__}")
        return 0

    if args.info:
        info = get_system_info()
        print(color("System Information:", "blue"))
        print(format_system_context(info))
        return 0

    if args.history is not None:
        entries = read_history(args.history)
        if not entries:
            print(color("No execution history found.", "yellow"))
            return 0
        print(color(f"Last {len(entries)} execution(s):\n", "blue"))
        for entry in entries:
            print(entry)
        return 0

    if not args.prompt:
        parser.print_help()
        return 1

    prompt = " ".join(args.prompt)

    # Root check (skip for dry-run)
    if not args.dry_run and os.geteuid() != 0:
        print(color("Error: RED-AI must be run as root for execution mode.", "red"))
        print("Use --dry-run to preview commands without root, or run as root.")
        return 1

    print(f"{color('Processing:', 'blue')} \"{prompt}\"")
    print(color("Analyzing...", "yellow"))

    response = get_response(prompt)

    # If intent is unclear, ask the user what they want to do
    if response.get("ask_action"):
        param = response["sysctl_param"]
        print(color(f"\nDetected sysctl parameter: {param}", "blue"))
        print(color("Could not determine the intended action.", "yellow"))
        action = prompt_choice(
            "What would you like to do with {}?".format(param),
            [
                {"label": "Check current value", "value": "check"},
                {"label": "Enable (set to 1)", "value": "enable"},
                {"label": "Disable (set to 0)", "value": "disable"},
                {"label": "Set to a specific value", "value": "set"},
            ],
        )
        if action == "check":
            response = {
                "description": "Check sysctl parameter {}".format(param),
                "category": "kernel",
                "commands": ["sysctl {}".format(param)],
                "risk_level": "low",
                "requires_reboot": False,
                "notes": "",
                "source": "local_commands",
            }
        elif action == "set":
            try:
                value = input(color("Enter value for {}: ".format(param), "yellow")).strip()
            except (EOFError, KeyboardInterrupt):
                print()
                return 1
            if not value:
                print(color("No value provided.", "red"))
                return 1
            from .local_commands import _validate_sysctl_value
            error = _validate_sysctl_value(param, value)
            if error:
                print(color(error, "red"))
                return 1
            response = {
                "description": "Set {} = {}".format(param, value),
                "category": "kernel",
                "commands": ["sysctl -w {}={}".format(param, value)],
                "risk_level": "medium",
                "requires_reboot": False,
                "notes": "",
                "source": "local_commands",
                "persist_mode": "ask",
                "sysctl_param": param,
                "sysctl_value": value,
                "sysctl_conf": "/etc/sysctl.d/99-{}.conf".format(param.split(".")[0]),
            }
        else:
            value = "1" if action == "enable" else "0"
            response = {
                "description": "{} {} (set to {})".format(
                    "Enable" if action == "enable" else "Disable", param, value),
                "category": "kernel",
                "commands": ["sysctl -w {}={}".format(param, value)],
                "risk_level": "medium",
                "requires_reboot": False,
                "notes": "",
                "source": "local_commands",
                "persist_mode": "ask",
                "sysctl_param": param,
                "sysctl_value": value,
                "sysctl_conf": "/etc/sysctl.d/99-{}.conf".format(param.split(".")[0]),
            }

    # Handle kdump enable with preflight checks
    if response.get("_handler") == "kdump_enable":
        response = _handle_kdump_enable(args.dry_run)
        if response is None:
            return 1

    if "error" in response:
        print(color(f"\n{response['error']}", "red"))
        return 1

    # Show source indicator
    source = response.get("source", "unknown")
    if source == "local_commands":
        print(color("[Source: Local Command Database]", "green"))
    elif source == "ollama":
        print(color("[Source: Ollama AI Engine]", "blue"))

    commands = response.get("commands", [])
    if not commands:
        print(color("\nNo commands generated for this request.", "yellow"))
        return 1

    description = response.get("description", "Execute configuration")
    risk_level = response.get("risk_level", "medium")
    requires_reboot = response.get("requires_reboot", False)
    notes = response.get("notes", "")

    # If this is a sysctl change, prompt for persistence mode
    if response.get("persist_mode") == "ask":
        param = response["sysctl_param"]
        value = response["sysctl_value"]
        conf_file = response["sysctl_conf"]

        mode = prompt_choice(
            "How should this change be applied?",
            [
                {"label": "Runtime + Persistent (recommended)", "value": "both"},
                {"label": "Runtime only (lost after reboot)", "value": "runtime"},
                {"label": "Persistent only (apply on next reboot or sysctl -p)", "value": "persistent"},
            ],
        )

        if mode == "runtime":
            commands = [f"sysctl -w {param}={value}"]
            description = f"Set {param} = {value} (runtime only)"
            notes = "Runtime only. This change will be lost after reboot."
        elif mode == "persistent":
            commands = [
                f"echo '{param} = {value}' >> {conf_file}",
                f"sysctl -p {conf_file}",
            ]
            description = f"Set {param} = {value} (persistent)"
            notes = f"Persistent via {conf_file}. Applied immediately with sysctl -p."
        else:
            commands = [
                f"sysctl -w {param}={value}",
                f"echo '{param} = {value}' >> {conf_file}",
            ]
            description = f"Set {param} = {value} (runtime + persistent)"
            notes = f"Runtime change is immediate. Persistent via {conf_file}."

    if notes:
        print(f"\n{color('Notes:', 'yellow')} {notes}")

    results = execute_commands(
        commands,
        dry_run=args.dry_run,
        skip_confirm=args.yes,
        risk_level=risk_level,
        description=description,
        requires_reboot=requires_reboot,
    )

    if results is not None:
        log_execution(
            prompt, commands, results,
            dry_run=args.dry_run,
            source=response.get("source", "unknown"),
            risk_level=risk_level,
            description=description,
            requires_reboot=requires_reboot,
            notes=notes,
        )

    return 0


def entry_point():
    sys.exit(main())


if __name__ == "__main__":
    entry_point()
