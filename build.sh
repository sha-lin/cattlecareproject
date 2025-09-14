#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Setting Python version..."
export PYTHON_VERSION=3.11.4

echo "Upgrading pip..."
python -m pip install --upgrade pip

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Running database migrations..."
python manage.py migrate

echo "Build completed successfully!"
