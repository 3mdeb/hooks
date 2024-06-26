import argparse
import os
import re
import sys
from importlib import metadata

NAME_RULES = {
    "Zarhus": "Zarhus",
    "Dasharo": "Dasharo",
    "coreboot": "coreboot",
    "Yocto": "Yocto",
    "NVIDIA": "NVIDIA",
    "UEFI": "UEFI",
}

COMMENT_STRINGS = {
    ".py": "#",
    ".md": "<!--",
    ".bb": "#",
    ".bbappend": "#",
    ".inc": "#",
    ".sh": "#",
    ".yaml": "#",
    ".yml": "#",
    "default": "#",
}

IGNORE_STRING = "namespell:disable"


def __get_comment_string(file) -> str:
    _, extension = os.path.splitext(f"./{file.name}")
    return (
        COMMENT_STRINGS[extension]
        if extension in COMMENT_STRINGS.keys()
        else COMMENT_STRINGS["default"]
    )


def __get_active_rules(
    filename, line, line_number, line_ignore_pattern, file_ignore_pattern
):
    are_file_rules = False
    # If the first line contains ignore statement ONLY, it applies to the whole
    # file
    if line_number == 1 and re.match(file_ignore_pattern, line):
        matched = True
        are_file_rules = True
    else:
        matched = re.match(line_ignore_pattern, line) is not None
    active_rules = NAME_RULES.copy()
    if matched:
        pattern = re.compile(r"namespell:disable\s*(.*)")
        match = pattern.search(line)
        # This should never happen
        if match is None:
            raise RegexParseError(f"Parse error: {line}")
        rules_to_disable = match.group(1)
        # Disable all rules in this line
        if re.match(r"namespell:disable\s*$", match.group(0).replace("-->", "")):
            active_rules = {}
        else:
            # Get rid of whitespaces and comment closing (markdown)
            to_disable_list = rules_to_disable.replace(" ", "").replace("-->", "")
            to_disable_list = to_disable_list.split(",")
            for rule in to_disable_list:
                removed = active_rules.pop(rule, None)
                if removed is None:
                    print(
                        f"Warning: {filename}:{line_number}: {rule} rule does not exist. Available rules: {list(NAME_RULES.keys())}"
                    )

    return active_rules, are_file_rules


def check_and_fix_file(filename, autofix=False):
    with open(filename, "r", encoding="utf8", errors="ignore") as file:
        lines = file.readlines()
        comment_string = __get_comment_string(file)

    # Don't check empty files
    if len(lines) == 0:
        return True
    fixed_lines = []
    found_issues = False
    file_ignore_pattern = rf"\s*{re.escape(comment_string)}\s*namespell:disable.*"
    line_ignore_pattern = rf".*{re.escape(comment_string)}\s*namespell:disable.*"

    active_rules, are_file_rules = __get_active_rules(
        filename, lines[0], 1, line_ignore_pattern, file_ignore_pattern
    )
    # If first line contains file-wide rules, set them
    file_rules = active_rules if are_file_rules else NAME_RULES.copy()
    # Whole file ignored
    if file_rules == {}:
        return True
    for line_number, line in enumerate(lines, start=1):
        fixed_line = line
        active_rules = file_rules
        if line_number != 1:
            line_rules, _ = __get_active_rules(
                filename, line, line_number, line_ignore_pattern, file_ignore_pattern
            )
            # Active rules are the rules that weren't disabled by the file-wide
            # and inline disabled rules, in other words the intersection of
            # active rules dicts
            active_rules = {
                key: line_rules[key] for key in line_rules if key in file_rules
            }

        for name, correct_format in active_rules.items():
            pattern = re.compile(
                rf"(?<![-_\./=\"#]){re.escape(name)}(?![-_\./=\"#])", re.IGNORECASE
            )
            matches = pattern.findall(line)
            for match in matches:
                if match != correct_format:
                    found_issues = True
                    print(
                        f"{filename}:{line_number}: '{match}' should be '{correct_format}'"
                    )
                if autofix:
                    fixed_line = re.sub(pattern, correct_format, fixed_line)
        fixed_lines.append(fixed_line)

    if found_issues and autofix:
        with open(filename, "w") as file:
            file.writelines(fixed_lines)

    return not found_issues


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Trademark name spell checker")
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=metadata.version("3mdeb-hooks"),
        help="Print package version",
    )
    parser.add_argument(
        "-f",
        "--fix",
        action="store_true",
        default=False,
        help="Automatically fix issues",
    )
    parser.add_argument("files", nargs="+", help="File(s) to parse")
    return parser.parse_args()


def main():
    args = parse_args()
    all_passed = True
    for filename in args.files:
        if not check_and_fix_file(filename, args.fix):
            all_passed = False
    if not all_passed:
        sys.exit(1)


if __name__ == "__main__":
    main()


class RegexParseError(Exception):
    pass
