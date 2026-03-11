import subprocess
import sys

COLORS = {
    "reset": "\033[0m",
    "red": "\033[1;31m",
    "green": "\033[1;32m",
    "yellow": "\033[1;33m",
    "blue": "\033[1;34m",
    "cyan": "\033[1;36m",
}


def color(text, c):
    return f"{COLORS.get(c, '')}{text}{COLORS['reset']}"


def confirm(message):
    try:
        response = input(color(f"{message} (yes/no): ", "yellow")).strip().lower()
        return response in ("yes", "y")
    except (EOFError, KeyboardInterrupt):
        print()
        return False


def execute_commands(commands, dry_run=False, skip_confirm=False, risk_level="medium",
                     description="", requires_reboot=False):
    results = []

    print(f"\n{color('=' * 60, 'cyan')}")
    print(color(f"  {description}", "cyan"))
    print(f"{color('=' * 60, 'cyan')}")
    print(f"{color('Risk Level:', 'blue')} {risk_level}")

    if requires_reboot:
        print(color("Warning: This configuration requires a system reboot.", "yellow"))

    if risk_level == "high":
        print(color("WARNING: This is a HIGH RISK operation!", "red"))

    print(f"\n{color('Commands to execute:', 'blue')}")
    for i, cmd in enumerate(commands, 1):
        print(f"  {i}. {cmd}")

    if dry_run:
        print(color("\n[DRY RUN MODE - Commands will not be executed]", "yellow"))
        for cmd in commands:
            results.append({"command": cmd, "status": "skipped", "output": ""})
        print(color("[DRY RUN COMPLETE - No commands were executed]", "yellow"))
        return results

    if not skip_confirm:
        if not confirm("\nDo you want to proceed?"):
            print(color("Operation cancelled by user.", "red"))
            return None

    print()
    success_count = 0
    failed_count = 0

    for i, cmd in enumerate(commands, 1):
        print(f"  {color(f'[{i}/{len(commands)}]', 'blue')} {cmd}")
        sys.stdout.flush()

        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=120
            )
            if result.returncode == 0:
                print(f"    {color('[OK]', 'green')}")
                status = "success"
                success_count += 1
            else:
                print(f"    {color('[FAILED]', 'red')}")
                status = "failed"
                failed_count += 1

            output = result.stdout + result.stderr
            if output.strip():
                for line in output.strip().split("\n"):
                    print(f"    {line}")

            results.append({"command": cmd, "status": status, "output": output})

        except subprocess.TimeoutExpired:
            print(f"    {color('[TIMEOUT]', 'red')}")
            results.append({"command": cmd, "status": "timeout", "output": ""})
            failed_count += 1

    print(f"\n{color('=== Execution Summary ===', 'cyan')}")
    print(f"Total commands: {len(commands)}")
    print(f"{color(f'Successful: {success_count}', 'green')}")
    if failed_count > 0:
        print(f"{color(f'Failed: {failed_count}', 'red')}")

    if requires_reboot:
        print(color("\nREMINDER: Please reboot the system for changes to take effect.", "yellow"))

    return results
