#!/usr/bin/env sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
venv_dir="$project_dir/.venv"

python3 -m venv "$venv_dir"
"$venv_dir/bin/python" -m pip install --upgrade pip
"$venv_dir/bin/python" -m pip install --editable "$project_dir"

echo "Installed UiA Spider-Robot in $venv_dir"
echo "Activate it with: . $venv_dir/bin/activate"
echo "Then test with: spider-robot --simulate walk forward --cycles 1"
