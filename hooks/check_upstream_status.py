#!/usr/bin/env python3


import argparse
import re
import subprocess
import sys

# Valid Upstream-Status patterns
UPSTREAM_STATUS_PATTERNS = [
    r"^Upstream-Status:\s+Backport\s+\[.+\]$",
    r"^Upstream-Status:\s+Inappropriate\s+\[.+\]$",
    r"^Upstream-Status:\s+Pending$",
    r"^Upstream-Status:\s+Submitted\s+\[.+\]$",
]


def get_commit_range(base_ref="origin/dasharo", debug=False):
    """Get the list of commits from base_ref (branch or commit) to HEAD."""
    try:
        subprocess.run(
            ["git", "fetch", "origin"], check=True, stdout=subprocess.DEVNULL
        )
        merge_base = (
            subprocess.check_output(["git", "merge-base", "HEAD", base_ref])
            .strip()
            .decode()
        )
        commits = (
            subprocess.check_output(["git", "rev-list", f"{merge_base}..HEAD"])
            .decode()
            .splitlines()
        )
        if debug:
            print(f"[DEBUG] Base ref: {base_ref}")
            print(f"[DEBUG] Merge base: {merge_base}")
            print(f"[DEBUG] Commits to check ({len(commits)}): {commits}")
        return commits
    except subprocess.CalledProcessError as e:
        print("Error getting commit range:", e, file=sys.stderr)
        sys.exit(1)


def has_valid_upstream_status(commit_hash, debug=False):
    """Check if commit contains a valid Upstream-Status line."""
    try:
        message = subprocess.check_output(
            ["git", "log", "--format=%B", "-n", "1", commit_hash]
        ).decode()
        if debug:
            print(f"\n[DEBUG] Commit: {commit_hash}\n{message.strip()}\n{'-' * 40}")
        for line in message.splitlines():
            for pattern in UPSTREAM_STATUS_PATTERNS:
                if re.match(pattern, line.strip()):
                    return True
        return False
    except subprocess.CalledProcessError as e:
        print(f"Error reading commit {commit_hash}:", e, file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Check commits for valid Upstream-Status tags."
    )
    parser.add_argument(
        "--base",
        type=str,
        default="origin/dasharo",
        help="Base branch or commit to compare against (default: origin/dasharo)",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    args = parser.parse_args()

    commits = get_commit_range(base_ref=args.base, debug=args.debug)
    failed_commits = []

    for commit in commits:
        if not has_valid_upstream_status(commit, debug=args.debug):
            failed_commits.append(commit)

    if failed_commits:
        print(
            "\n❌ The following commits are missing or have invalid 'Upstream-Status':\n"
        )
        for fc in failed_commits:
            print(f"  - {fc}")
        print("\nExpected format examples:")
        print("  Upstream-Status: Backport [CB:86758]")
        print("  Upstream-Status: Inappropriate [Dasharo downstream]")
        print("  Upstream-Status: Pending")
        print("  Upstream-Status: Submitted [CB:86758]")
        sys.exit(1)
    else:
        print("✅ All commits contain a valid 'Upstream-Status' tag.")


if __name__ == "__main__":
    main()
