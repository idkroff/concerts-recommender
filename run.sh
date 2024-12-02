#!/bin/bash

SCRIPT_PATH=$(dirname "$(realpath "$0")")
. "$SCRIPT_PATH/venv/bin/activate"
pip3 install -r "$SCRIPT_PATH/app/requirements.txt"

python "$SCRIPT_PATH/main.py"
