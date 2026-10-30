#!/usr/bin/env python3
import subprocess
import sys

def run_command(command):
    """Runs a command and captures its stdout, stderr, and exit status."""
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return None


def green(text):
    """Returns text colored in green."""
    return f"\033[92m{text}\033[0m"


def yellow(text):
    """Returns text colored in yellow."""
    return f"\033[93m{text}\033[0m"


def red(text):
    """Returns text colored in red."""
    return f"\033[91m{text}\033[0m"


def validate(command):
    """Validates a command silently and prints an error message if it fails."""
    if not run_command(command):
        return False
    return True


def check_health():
    """Checks the system health by validating necessary tools with structured data."""
    validation_steps = [
        {
            "command": "make --version",
            "error": "make is not installed",
            "hint": "Win: choco install make",
            "url": "https://makefiletutorial.com/"
        },
        {
            "command": "git --version",
            "error": "git is not installed",
            "hint": "Mac: brew install git",
            "url": "https://git-scm.com - "
        },
        {
            "command": "uv --version",
            "error": "uv is not installed",
            "hint": "Mac: brew install uv, Win: scoop install uv",
            "url": "https://docs.astral.sh/uv/getting-started/installation/"
        },
        {
            "command": "pre-commit --version",
            "error": "pre-commit is not installed",
            "hint": "uv tool install pre-commit",
            "url": "https://pre-commit.com"
        },
        {
            "command": "mkdocs --version",
            "error": "mkdocs is not installed",
            "hint": "uv tool install mkdocs",
            "url": "https://www.mkdocs.org/getting-started/"
        },
        {
            "command": "uv tool list --show-with | grep mkdocs | grep mkdocs-techdocs-core",
            "error": "mkdocs is missing the techdocs plugin",
            "hint": "uv tool install mkdocs --with mkdocs-techdocs-core",
            "url": "https://github.com/backstage/mkdocs-techdocs-core"
        }
    ]

    for step in validation_steps:
        if not validate(step['command']):
            print(red(f"ERROR: {step['error']}"))
            if "hint" in step and step["hint"]:
                print(f"Try: {yellow(step['hint'])}")
            if "url" in step and step['url']:
                print(f"See: {step['url']}")
            sys.exit(1)

    print(green("Hooray! You seem to be OK 🎉"))


if __name__ == "__main__":
    check_health()