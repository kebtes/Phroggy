#!/bin/bash
set -e

echo "Starting setup..."

# check python3 and pip
command -v python3 >/dev/null 2>&1 || { echo >&2 "Python3 is not installed. Aborting."; exit 1; }

# check if poetry is installed; if not, install it
if ! command -v poetry >/dev/null 2>&1; then
    echo "Poetry is not installed. Installing..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
fi

echo "Installing dependencies from pyproject.toml with Poetry..."
poetry install --no-interaction --no-ansi

echo "Setup completed successfully."