#!/bin/bash
echo "Installing dependencies..."
pip install -r requirements.txt
echo "Starting AJFX Trading Radar on port 8011..."
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8011 --reload
