import argparse
import os
import re
import sys
import time
from collections import deque
from importlib import metadata
from typing import List, NamedTuple

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


class IgnoreBlock(NamedTuple):
    start: str
    end: str


class IgnoreInline(NamedTuple):
    start: str
    end: str


IGNORE_BLOCKS = {
    ".md": [IgnoreBlock("```", "```"), IgnoreBlock("<!--", "-->")],
    "default": [],
}

IGNORE_INLINE = {
    ".md": [IgnoreInline("`", "`"), IgnoreInline("<!--", "-->")],
    "default": [],
}

# Stack that keeps track of "active" blocks to be ignored by storing their
# start strings. This is necessary for nested blocks (e.g code block inside
# comment)
blocks = deque()
current_start_token = ""


def __get_comment_string(extension) -> str:
    return (
        COMMENT_STRINGS[extension]
        if extension in COMMENT_STRINGS.keys()
        else COMMENT_STRINGS["default"]
    )


def __get_ignore_blocks(extension) -> List[IgnoreBlock]:
    return (
        IGNORE_BLOCKS[extension]
        if extension in IGNORE_BLOCKS.keys()
        else IGNORE_BLOCKS["default"]
    )


def __get_inline_ignore(extension) -> List[IgnoreInline]:
    return (
        IGNORE_INLINE[extension]
        if extension in IGNORE_INLINE.keys()
        else IGNORE_INLINE["default"]
    )


def __log_verbose(message, verbose):
    if verbose:
        print(message)


# Check if the line starts/ends a block to be ignored and modify the blocks
# stack accordingly
def __check_block(ignore_blocks, line, verbose=False):
    global current_start_token
    for ignore_block in ignore_blocks:
        start_index = line.find(ignore_block.start)
        end_index = line.find(ignore_block.end)
        if start_index != -1:
            # For identical start and end tokens: If the last start token was
            # the same as this one, then this one is an end token
            if (
                ignore_block.start == ignore_block.end
                and current_start_token == ignore_block.start
            ):
                start_index = -1
            else:
                __log_verbose(
                    f"BLOCK START: {ignore_block.start}, INDEX: {start_index}", verbose
                )
                blocks.append(ignore_block.start)
                current_start_token = ignore_block.start
        # Check if block end matches the latest block start token
        # If true, remove it from the stack
        if end_index != -1 and end_index != start_index:
            __log_verbose(f"BLOCK END: {ignore_block.end}, INDEX: {end_index}", verbose)
            if current_start_token == ignore_block.start:
                current_start_token = ""
                try:
                    blocks.pop()
                    if blocks:
                        # Get element from the top without popping it
                        current_start_token = blocks[-1]
                except IndexError:
                    return


# return list of indices of words to be ignored
def __check_inline_ignore(ignore_inline, line, verbose=False):
    indices = []
    for element in ignore_inline:
        start_index = line.find(element.start)
        if start_index == -1:
            continue
        position = 0
        line_to_process = line
        while start_index != -1:
            __log_verbose(f"INLINE BLOCK START: {position + start_index}", verbose)
            position += start_index
            line_to_process = line_to_process[start_index + 1 :]
            end_index = line_to_process.find(element.end) + 1
            if end_index == -1:
                print("Error: No matching inline comment/code ending tag")
            __log_verbose(f"INLINE BLOCK END: {position + end_index}", verbose)
            line_slice = line_to_process[: end_index - 1]
            for name in NAME_RULES.keys():
                pattern = re.compile(
                    rf"(?<![-_\./=\"#]){re.escape(name)}(?![-_\./=\"#])", re.IGNORECASE
                )
                for m in re.finditer(pattern, line_slice):
                    i = position + m.start() + 1
                    indices.append(i)
            position += end_index + 1
            line_to_process = line_to_process[end_index:]
            start_index = line_to_process.find(element.start)
    return indices


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


def check_and_fix_file(filename, autofix=False, verbose=False):
    with open(filename, "r", encoding="utf8", errors="ignore") as file:
        lines = file.readlines()
        _, extension = os.path.splitext(f"./{file.name}")
        comment_string = __get_comment_string(extension)
        ignore_blocks = __get_ignore_blocks(extension)
        ignore_inline = __get_inline_ignore(extension)
        __log_verbose(f"FILE: {filename}", verbose)

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
        __log_verbose(f"LINE {line_number}", verbose)
        fixed_line = line
        __check_block(ignore_blocks, line, verbose)
        to_ignore = __check_inline_ignore(ignore_inline, line, verbose)
        if blocks:
            fixed_lines.append(fixed_line)
            continue
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
            matches = re.finditer(pattern, line)
            for match in matches:
                __log_verbose(f"FOUND: {match.group()} AT {match.start()}", verbose)
                if match.group() != correct_format and match.start() not in to_ignore:
                    found_issues = True
                    print(
                        f"{filename}:{line_number}: '{match.group()}' should be '{correct_format}'"
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
    parser.add_argument(
        "--verbose", action="store_true", default=False, help="Run tool in verbose mode"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    all_passed = True
    for filename in args.files:
        if not check_and_fix_file(filename, args.fix, args.verbose):
            all_passed = False
    if not all_passed:
        sys.exit(1)


if __name__ == "__main__":
    main()


class RegexParseError(Exception):
    pass
