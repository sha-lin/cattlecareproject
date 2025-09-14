#!/bin/bash

echo "=== Minimal Vercel Build ==="

# Install dependencies
echo "Installing minimal dependencies..."
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "=== Build completed ==="
