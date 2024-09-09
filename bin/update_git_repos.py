#!/usr/bin/env python3

import os
import subprocess

from update_gitignore import update_gitignore


def run_command(command):
    """Runs a shell command and returns its output and error status."""
    result = subprocess.run(
        command, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    return result.stdout, result.stderr, result.returncode


def update(directory, repo_name):
    """Updates the repository by pulling new changes."""
    print(f"Updating {repo_name}... ", end="")
    output, error, status = run_command(f"git -C {directory} pull --rebase")
    handle_response(output, error, status)


def clone(repo_name):
    """Clones the repository."""
    print(f"Cloning {repo_name}... ", end="")
    output, error, status = run_command(
        f"git clone git@github.com:statisticsnorway/{repo_name}.git"
    )
    if status != 0 and "Permission denied (publickey)" in error:
        print("SSH not configured, falling back to GH CLI tool.", end="")
        output, error, status = run_command(
            f"gh repo clone statisticsnorway/{repo_name}"
        )
    handle_response(output, error, status)


def handle_response(output, error, status):
    """Handles the output based on the git command result."""
    if status == 0:
        if "up-to-date" in output:
            print(green("Already up-to-date"))
        elif "Cloning" in output:
            print(green("OK"))
        else:
            print(green("OK"))
            print(output, "\n")
    else:
        print(red("ERROR"))
        print(error, "\n")


def green(text):
    """Returns text colored in green."""
    return f"\033[92m{text}\033[0m"


def red(text):
    """Returns text colored in red."""
    return f"\033[91m{text}\033[0m"


def main():
    current_repo = os.path.basename(os.getcwd())
    update(".", current_repo)

    with open("git-repos.txt", "r") as file:
        for repo in file:
            repo = repo.strip()
            if repo and os.path.isdir(repo):
                update(repo, repo)
            else:
                clone(repo)

    update_gitignore(".gitignore", "git-repos.txt")


if __name__ == "__main__":
    main()
