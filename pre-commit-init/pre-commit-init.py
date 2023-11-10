#!/usr/bin/env python3

import os
import subprocess
import sys
from shutil import copy2

from jinja2 import Environment, FileSystemLoader


def main(repo_path, categories):
    # Navigate to the repository path
    os.chdir(repo_path)

    # Check if .pre-commit-config.yaml already exists
    if os.path.exists(".pre-commit-config.yaml"):
        should_continue = input(
            ".pre-commit-config.yaml already exists. Do you want to continue? (y/N): "
        )
        if not should_continue.lower().startswith("y"):
            sys.exit(1)

    # Define the valid categories
    valid_categories = {"markdown", "bash", "python", "robotframework"}

    # Validate the input categories
    for category in categories:
        if category not in valid_categories:
            print(f"Error: Unknown hook category '{category}'")
            sys.exit(1)

    # Set up the Jinja2 environment and render the template
    script_dir = os.path.dirname(os.path.abspath(__file__))
    env = Environment(
        loader=FileSystemLoader(script_dir),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("pre_commit_config.j2")
    with open(".pre-commit-config.yaml", "w") as f:
        f.write(template.render(categories=categories))

    # Install additional configuration files based on the selected categories
    copy2(os.path.join(script_dir, ".yamllint"), repo_path)
    copy2(os.path.join(script_dir, ".conform.yaml"), repo_path)
    copy2(os.path.join(script_dir, ".codespellrc"), repo_path)
    copy2(os.path.join(script_dir, ".codespellx"), repo_path)
    if "markdown" in categories:
        copy2(os.path.join(script_dir, ".markdownlint.yaml"), repo_path)

    # Run pre-commit commands
    subprocess.run(["pre-commit", "validate-config"])
    subprocess.run(["pre-commit", "install"])
    subprocess.run(["pre-commit", "autoupdate"])


if __name__ == "__main__":
    # Display help message if no or incorrect arguments are given
    if len(sys.argv) < 3:
        print("Usage: python3 script.py <repo_path> <categories>")
        print("Categories: markdown, bash, python, robotframework")
        sys.exit(1)

    # Expecting the repo path as the first argument and a space-separated list of categories as the second
    repo_path = sys.argv[1]
    categories = sys.argv[2].split()
    main(repo_path, categories)
