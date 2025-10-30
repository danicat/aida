#!/bin/bash
set -e

echo "========================================"
echo " AIDA - Project Cleanup"
echo "========================================"
echo "This script will remove all generated data, models, and repositories."
read -p "Are you sure you want to continue? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Cleanup cancelled."
    exit 1
fi

echo "[1/4] Removing osquery data..."
rm -rf osquery_data

echo "[2/4] Removing downloaded models..."
rm -rf models

echo "[3/4] Removing SQLite database..."
rm -f osquery.db

echo "[4/4] Cleaning Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

echo "========================================"
echo " Cleanup Complete!"
echo "========================================"
