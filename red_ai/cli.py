#!/usr/bin/env python3
import argparse
import os
import sys

from . import __version__
from .ai_engine import get_ai_response
from .executor import execute_commands, color, prompt_choice
from .logger import log_execution, read_history
from .system_info import get_system_info, format_system_context


def _build_banner():
    lines = [
        "",
        f"RED-AI Configuration Assistant v{__version__}",
        "",
        "AI-powered system configuration tool for RHEL Linux",
        "Developed by: Natesh Sharma",
        "",
    ]
    inner = max(len(line) for line in lines) + 6
    top = "╔" + "═" * inner + "╗"
    bot = "╚" + "═" * inner + "╝"
    mid = ["║" + line.center(inner) + "║" for line in lines]
    return "\n" + "\n".join([color(l, "cyan") for l in [top] + mid + [bot]]) + "\n"


BANNER = _build_banner()


def get_response(prompt):
    """Get AI response for the prompt."""
    return get_ai_response(prompt)


def main():
    parser = argparse.ArgumentParser(
        prog="red-ai",
        description="AI-powered RHEL configuration tool",
    )
    parser.add_argument("prompt", nargs="*", help="Configuration request in plain English")
    parser.add_argument("-d", "--dry-run", action="store_true", help="Preview commands without executing")
    parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation prompts")
    parser.add_argument("-v", "--version", action="store_true", help="Show version")
    parser.add_argument("-i", "--info", action="store_true", help="Show system information")
    parser.add_argument("--history", nargs="?", const=10, type=int, metavar="N",
                        help="Show last N executions (default: 10)")

    args = parser.parse_args()

    if args.version:
        print(BANNER)
        return 0

    if args.info:
        print(BANNER)
        info = get_system_info()
        print(color("System Information:", "blue"))
        print(format_system_context(info))
        return 0

    if args.history is not None:
        print(BANNER)
        entries = read_history(args.history)
        if not entries:
            print(color("No execution history found.", "yellow"))
            return 0
        print(color(f"Last {len(entries)} execution(s):\n", "blue"))
        for entry in entries:
            print(entry)
        return 0

    if not args.prompt:
        print(BANNER)
        parser.print_help()
        return 1

    prompt = " ".join(args.prompt)

    print(BANNER)

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

    if "error" in response:
        print(color(f"\n{response['error']}", "red"))
        return 1

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
