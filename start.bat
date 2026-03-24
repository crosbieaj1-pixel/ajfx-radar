@echo off
setlocal

cd /d %~dp0

if exist venv\Scripts\activate.bat call venv\Scripts\activate.bat
if exist .venv\Scripts\activate.bat call .venv\Scripts\activate.bat

set REQ_FILE=backend\requirements.txt
if not exist %REQ_FILE% set REQ_FILE=requirements.txt

python -c "import fastapi, uvicorn" >nul 2>nul
if errorlevel 1 (
    echo Installing dependencies from %REQ_FILE%...
    pip install -r %REQ_FILE%
)

echo Starting AJFX Trading Radar on port 8011...
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8011 --reload
