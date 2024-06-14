import sys
import re

NAME_RULES = {
    'Zarhus': 'Zarhus',
    'Dasharo': 'Dasharo',
    'coreboot': 'coreboot',
    'Yocto': 'Yocto',
}

def check_and_fix_trademark(filename, autofix=False):
    with open(filename, 'r') as file:
        lines = file.readlines()

    fixed_lines = []
    found_issues = False

    for line_number, line in enumerate(lines, start=1):
        fixed_line = line
        for name, correct_format in NAME_RULES.items():
            pattern = re.compile(rf'(?<![-_]){re.escape(name)}(?![-_])', re.IGNORECASE)
            matches = pattern.findall(line)
            for match in matches:
                if match != correct_format:
                    found_issues = True
                    print(f"{filename}:{line_number}: '{match}' should be '{correct_format}'")
                if autofix:
                    fixed_line = re.sub(pattern, correct_format, fixed_line)
        fixed_lines.append(fixed_line)

    if found_issues and autofix:
        with open(filename, 'w') as file:
            file.writelines(fixed_lines)

    return not found_issues

