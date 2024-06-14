#!/bin/bash

SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
cd "$SCRIPT_DIR/namespell" || exit 1
pip install .
cd - || exit 1
namespell "$@"
