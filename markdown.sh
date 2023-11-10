#!/usr/bin/env bash

CONFIG_DIR="$HOME/.config/3mdeb-hooks"

errorExit() {
    errorMessage="$1"
    echo "$errorMessage"
    exit 1
}

errorCheck() {
    errorCode=$?
    errorMessage="$1"
    [ "$errorCode" -ne 0 ] && errorExit "$errorMessage : ($errorCode)"
}

usage() {
cat <<EOF
Usage: ./$(basename "${0}") <command> <file>
This script verifies the markdown file against our guidelines.
  Commands:
    check     run the linter
    fix       also try to fix some errors automatically
EOF
  exit 0
}

MARKDOWNLINT_CONTAINER="ghcr.io/igorshubovych/markdownlint-cli:v0.32.2"

check() {
  docker run \
    -v "$CONFIG_DIR"/.markdownlint.yaml:/workdir/.markdownlint.yaml:ro \
    -v "$FULL_PATH":/workdir/"$FILE_NAME":ro \
    "$MARKDOWNLINT_CONTAINER" \
    -c .markdownlint.yaml "$FILE_NAME"
}

fix() {
  docker run \
    -v "$CONFIG_DIR"/.markdownlint.yaml:/workdir/.markdownlint.yaml:ro \
    -v "$FULL_PATH":/workdir/"$FILE_NAME":rw \
    "$MARKDOWNLINT_CONTAINER" \
    -c .markdownlint.yaml --fix "$FILE_NAME"
}

CMD="$1"
FILE="$2"

if [ -z "$CMD" ]; then
  echo "command not given"
  usage
fi

if [ -z "$FILE" ]; then
  echo "file not given"
  usage
fi

FULL_PATH="$(readlink -f "$FILE")"
FILE_NAME="$(basename "$FULL_PATH")"


case "$CMD" in
    "check")
      check
        ;;
    "fix")
      fix
        ;;
    *)
        echo "Invalid command: \"$CMD\""
        usage
        ;;
esac
