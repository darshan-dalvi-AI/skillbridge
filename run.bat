@echo off
title SkillBridge Launcher
cd /d "%~dp0"

echo ===============================================
echo    SkillBridge  -  AI Career ^& Skill-Gap App
echo ===============================================
echo.

echo [1/3] Checking Python...
where py >nul 2>nul
if %errorlevel%==0 (
    set "PYCMD=py"
) else (
    set "PYCMD=python"
)
%PYCMD% --version
if errorlevel 1 (
    echo.
    echo ERROR: Python was not found on PATH.
    echo Install Python 3 from python.org, then run this file again.
    echo.
    pause
    exit /b 1
)
echo.

echo [2/3] Installing required packages (first run can take 1-2 minutes)...
%PYCMD% -m pip install -r requirements.txt
echo.

echo Preparing Streamlit (skipping first-run email prompt)...
if not exist "%USERPROFILE%\.streamlit" mkdir "%USERPROFILE%\.streamlit"
if not exist "%USERPROFILE%\.streamlit\credentials.toml" (
    > "%USERPROFILE%\.streamlit\credentials.toml" echo [general]
    >> "%USERPROFILE%\.streamlit\credentials.toml" echo email = ""
)
echo.

echo [3/4] Starting the backend API (SQLite) on port 8000 in a new window...
start "SkillBridge API (keep open)" cmd /k "%PYCMD% -m uvicorn backend.main:app --host 127.0.0.1 --port 8000"
echo Waiting a few seconds for the backend to come up...
timeout /t 4 >nul
echo.
echo [4/4] Launching SkillBridge in your browser (port 8510)...
echo Keep THIS window open while using the app. Close it to stop the app.
echo (A second window runs the backend API - close it too when you are done.)
echo.
%PYCMD% -m streamlit run app.py --server.port 8510

echo.
echo (SkillBridge has stopped.)
pause
