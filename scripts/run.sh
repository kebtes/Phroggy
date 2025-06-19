#!/bin/bash
set -e

echo "Activating virtual environment and starting Phroggy..."
source venv/bin/activate

python -m bot.main