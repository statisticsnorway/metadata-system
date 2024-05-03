#!/usr/bin/env python3
import os

def update_gitignore(gitignore_path, repos_file):
    """Update the .gitignore file with new entries from the repos file."""
    try:
        # Load current .gitignore entries and prepare new entries
        with open(gitignore_path, 'r+') as gitignore_file:
            existing_lines = set(gitignore_file.read().strip().split('\n'))
            gitignore_file.seek(0, os.SEEK_END)  # Move cursor to the end for appending

            with open(repos_file, 'r') as repos_file:
                for line in repos_file:
                    repo_entry = line.strip() + '/'
                    if repo_entry and repo_entry not in existing_lines:
                        gitignore_file.write(repo_entry + '\n')
                        existing_lines.add(repo_entry)  # Update set to include new entry

    except FileNotFoundError:
        print(f"File not found: {gitignore_path} or {repos_file}")
    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    update_gitignore('.gitignore', 'git-repos.txt')

if __name__ == "__main__":
    main()
