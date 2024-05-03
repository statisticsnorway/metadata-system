#!/usr/bin/env python3

import re
import subprocess

def strip_ansi_codes(text):
    # ANSI escape sequences regex pattern
    ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', text)


def replace_section(file_path, start_marker, end_marker, new_content):
    with open(file_path, 'r+') as file:
        content = file.read()
        pattern = re.compile(re.escape(start_marker) + '.*?' + re.escape(end_marker), re.DOTALL)
        new_text = f"{start_marker}{new_content}{end_marker}"
        updated_content = re.sub(pattern, new_text, content)
        file.seek(0)
        file.write(updated_content)
        file.truncate()

# Update make help section in README.md
output = subprocess.run(['make', 'help'], stdout=subprocess.PIPE).stdout.decode('utf-8')
make_help_content = f"\n```\n{strip_ansi_codes(output)}```\n"
replace_section('README.md', '<!-- make-help-start -->', '<!-- make-help-end -->', make_help_content)

# Update linked repos section in README.md
with open('git-repos.txt', 'r') as file:
    repos = file.readlines()
    linked_repos_content = "".join(f"* [{repo.strip()}](https://github.com/statisticsnorway/{repo.strip()})\n" for repo in repos if repo.strip())
replace_section('README.md', '<!-- linked-repos-start -->', '<!-- linked-repos-end -->', f"\n{linked_repos_content}")
