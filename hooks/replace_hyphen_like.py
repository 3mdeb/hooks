#!/usr/bin/env python3
"""Replace hyphen-like characters with HYPHEN-MINUS (U+002D) in files."""

import argparse
import sys
from pathlib import Path


def replace_em_dash(file_path):
    """Replace hyphen-like characters with standard hyphens in a file."""
    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content

        # Replace various hyphen-like characters with HYPHEN-MINUS (U+002D)
        replacements = [
            ("\u2014", "\u002D"),  # EM DASH (—) → HYPHEN-MINUS (-)
            ("\u2013", "\u002D"),  # EN DASH (–) → HYPHEN-MINUS (-)
            ("\u2212", "\u002D"),  # MINUS SIGN (−) → HYPHEN-MINUS (-)
            ("\u2010", "\u002D"),  # HYPHEN (‐) → HYPHEN-MINUS (-)
            ("\u2011", "\u002D"),  # NON-BREAKING HYPHEN (‑) → HYPHEN-MINUS (-)
            ("\u2012", "\u002D"),  # FIGURE DASH (‒) → HYPHEN-MINUS (-)
            ("\u2015", "\u002D"),  # HORIZONTAL BAR (―) → HYPHEN-MINUS (-)
            ("\uFE58", "\u002D"),  # SMALL EM DASH (﹘) → HYPHEN-MINUS (-)
            ("\uFE63", "\u002D"),  # SMALL HYPHEN-MINUS (﹣) → HYPHEN-MINUS (-)
            ("\uFF0D", "\u002D"),  # FULLWIDTH HYPHEN-MINUS (－) → HYPHEN-MINUS (-)
        ]

        for old_char, new_char in replacements:
            content = content.replace(old_char, new_char)

        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
            print(f"Fixed hyphen-like characters in: {file_path}")
            return 1  # File was modified

        return 0  # No changes needed

    except Exception as e:
        print(f"Error processing {file_path}: {e}", file=sys.stderr)
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Replace hyphen-like characters with HYPHEN-MINUS"
    )
    parser.add_argument("files", nargs="*", help="Files to process")
    args = parser.parse_args()

    modified_count = 0
    for file_path in args.files:
        path = Path(file_path)
        if path.exists() and path.is_file():
            modified_count += replace_em_dash(path)

    if modified_count > 0:
        print(f"Modified {modified_count} file(s)")
        sys.exit(1)  # Exit with error code to fail pre-commit

    sys.exit(0)


if __name__ == "__main__":
    main()
