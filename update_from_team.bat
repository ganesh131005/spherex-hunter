@echo off
setlocal
chcp 65001 > nul
title Team RIP - 1-Click Multi-Track Sync and Radar

echo ==============================================================================
echo        TEAM RIP: 1-CLICK MULTI-TRACK GIT SYNC AND RADAR
echo        NASA Space Apps Challenge 2026 - SPHEREx Hunter
echo ==============================================================================
echo.
echo [1/3] Fetching all latest updates across all 5 team branches...
git fetch --all --prune

echo.
echo [2/3] Checking current branch and updating...
for /f "tokens=*" %%i in ('git branch --show-current') do set CURRENT_BRANCH=%%i

if "%CURRENT_BRANCH%"=="" set CURRENT_BRANCH=main

if "%CURRENT_BRANCH%"=="main" (
    echo   Pulling latest main branch from GitHub...
    git pull origin main --no-edit
) else (
    echo   Merging latest updates from origin/main into [%CURRENT_BRANCH%]...
    git merge origin/main --no-edit
)

echo.
echo [3/3] Generating Team Activity and GitHub Task Summary...
echo.
python tools\team_sync_summary.py

echo.
echo ==============================================================================
echo   SYNC COMPLETE! You now have everyone's latest code and tasks.
echo ==============================================================================
echo.
pause
