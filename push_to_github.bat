@echo off
title SkillBridge - Push to GitHub
cd /d "%~dp0"

echo ============================================================
echo   Pushing SkillBridge to GitHub
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

if not exist ".git" (
  echo Initializing git repository...
  git init
)

git config user.email "darshanydalvi2005@gmail.com"
git config user.name  "Darshan Dalvi"

echo Staging files (secrets, *.db and local data are ignored by .gitignore)...
git add -A
git commit -m "SkillBridge - AI Career Guidance + Skill-Gap Analyzer"

git branch -M main
git remote remove origin 1>nul 2>nul
git remote add origin https://github.com/darshan-dalvi-AI/skillbridge.git

echo.
echo Pushing to GitHub...
echo (If a "Sign in to GitHub" window pops up, click it and authorize - that is normal.)
echo.
git push -u origin main

echo.
if errorlevel 1 (
  echo ------------------------------------------------------------
  echo  PUSH FAILED. Scroll up and read the red/error text, or copy
  echo  it and paste it to Claude and we will fix it together.
  echo ------------------------------------------------------------
) else (
  echo ------------------------------------------------------------
  echo  SUCCESS! Your code is now on GitHub:
  echo  https://github.com/darshan-dalvi-AI/skillbridge
  echo ------------------------------------------------------------
)
echo.
pause
