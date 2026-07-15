@echo off
title SkillBridge - Build skill embedding index
cd /d "%~dp0"

echo ============================================================
echo   Building the skill-embedding index (skill_embeddings.json)
echo   This calls OpenRouter (batched) and takes about a minute.
echo   Your OPENROUTER_API_KEY is read from .streamlit\secrets.toml automatically.
echo ============================================================
echo.

rem --- find a Python launcher ---
set "PY="
where py  >nul 2>nul && set "PY=py"
if not defined PY ( where python >nul 2>nul && set "PY=python" )
if not defined PY (
  echo ERROR: Python was not found on PATH.
  echo Install Python 3, or run:  python build_embeddings.py
  echo.
  pause
  exit /b 1
)

echo Making sure the HTTP library is installed...
%PY% -m pip install --quiet --disable-pip-version-check requests

echo.
echo Building index...
%PY% build_embeddings.py

echo.
if exist "skill_embeddings.json" (
  echo ------------------------------------------------------------
  echo  SUCCESS! skill_embeddings.json is ready.
  echo  Now double-click push_fixes.bat to commit ^& push it,
  echo  then reload the app and toggle "Smart semantic detection".
  echo ------------------------------------------------------------
) else (
  echo ------------------------------------------------------------
  echo  No index file was created. Scroll up for the error, or
  echo  paste it to Claude and we'll fix it.
  echo ------------------------------------------------------------
)
echo.
pause
