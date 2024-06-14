import sys
import argparse
from importlib import metadata

from namespell.namespell_check import check_and_fix_trademark


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Trademark name spell checker")
    parser.add_argument("-v", "--version", action="version",
                        version=metadata.version("namespell"), help="Print package version")
    parser.add_argument("-f", "--fix", action="store_true",
                        default=False, help="Automatically fix issues")
    parser.add_argument("files", nargs="+", help="File(s) to parse")
    return parser.parse_args()


def main():
    args = parse_args()
    all_passed = True
    for filename in args.files:
        if not check_and_fix_trademark(filename, args.fix):
            all_passed = False
    if not all_passed:
        sys.exit(1)


if __name__ == "__main__":
    main()
