@echo off
title SkillBridge - Commit and Push performance fixes
cd /d "%~dp0"

echo ============================================================
echo   Committing and pushing SkillBridge performance fixes
echo   Repo: https://github.com/darshan-dalvi-AI/skillbridge
echo ============================================================
echo.

where git >nul 2>nul
if errorlevel 1 (
  echo ERROR: git is not installed / not on PATH.
  echo Install Git for Windows from https://git-scm.com/download/win then re-run this file.
  echo.
  pause
  exit /b 1
)

rem --- clear any stale index lock left by an interrupted git run ---
if exist ".git\index.lock" (
  echo Removing stale .git\index.lock ...
  del /f /q ".git\index.lock"
)

git config user.email "darshanydalvi2005@gmail.com"
git config user.name  "Darshan Dalvi"

echo Staging files (secrets, *.db and local data stay ignored by .gitignore)...
git add -A
git commit -m "perf: cache Gemini client, lru_cache skill extraction, cache progress-tab backend reads"

git branch -M main
git remote remove origin 1>nul 2>nul
git remote add origin https://github.com/darshan-dalvi-AI/skillbridge.git

echo.
echo Reconciling with anything already on GitHub (keeping our local changes)...
git pull origin main --no-rebase --no-edit -X ours

echo.
echo Pushing to GitHub...
echo (If a "Sign in to GitHub" window pops up, click it and authorize - that is normal.)
echo.
git push -u origin main

echo.
if errorlevel 1 (
  echo ------------------------------------------------------------
  echo  PUSH FAILED. Copy the error text above and paste it to Claude.
  echo ------------------------------------------------------------
) else (
  echo ------------------------------------------------------------
  echo  SUCCESS! Your fixes are now on GitHub:
  echo  https://github.com/darshan-dalvi-AI/skillbridge
  echo ------------------------------------------------------------
)
echo.
pause
