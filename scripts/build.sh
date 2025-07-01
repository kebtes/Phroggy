#!/bin/bash

set -e
set -x

echo "Starting build process..."

pip install --no-cache-dir poetry

poetry install --no-root --no-interaction --no-ansi

echo "Build process completed successfully."