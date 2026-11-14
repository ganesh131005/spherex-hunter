@echo off
setlocal
chcp 65001 > nul
title Team RIP - Safe Team Radar and Updates

echo ==============================================================================
echo        TEAM RIP: 1-CLICK SAFE TEAM RADAR AND UPDATES
echo        NASA Space Apps Challenge 2026 - SPHEREx Hunter
echo ==============================================================================
echo.
echo [1/2] Fetching team progress from GitHub (100%% safe, read-only)...
git fetch --all --prune
if %ERRORLEVEL% NEQ 0 (
    echo [!] Network or Git warning. Continuing with local data...
)

echo.
echo [2/2] Generating Multi-Track Activity and GitHub Tasks Dashboard...
echo.
python tools\team_sync_summary.py

echo.
echo ==============================================================================
echo                      SAFETY AND LOCAL WORK CHECK
echo ==============================================================================

REM Check if there are any uncommitted local changes
for /f "tokens=*" %%i in ('git status --porcelain') do set HAS_UNCOMMITTED=1

for /f "tokens=*" %%i in ('git branch --show-current') do set CURRENT_BRANCH=%%i
if "%CURRENT_BRANCH%"=="" set CURRENT_BRANCH=main

if defined HAS_UNCOMMITTED (
    echo [!] NOTE: You have uncommitted work in progress on [%CURRENT_BRANCH%].
    echo     Your files were NOT touched or modified. Your work is 100%% safe!
    echo.
    echo     When you are ready to save your work to GitHub, run:
    echo        sync_my_work.bat
    echo.
    goto :DONE
)

if "%CURRENT_BRANCH%"=="main" (
    echo Your working folder is clean.
    set /p MERGE_CHOICE="Pull latest main updates into your local folder? [Y/N] (Default=Y): "
    if /i "%MERGE_CHOICE%"=="N" goto :DONE
    echo Pulling latest main...
    git pull origin main --no-edit
    goto :DONE
)

echo Your working folder on branch [%CURRENT_BRANCH%] is clean.
echo.
echo Other teammates work on isolated branches:
echo   - darkodu  - backend/
echo   - coolodu  - frontend/
echo   - iceodu   - image_engine/
echo   - astrodu  - docs/
echo.
set /p MERGE_CHOICE="Do you want to merge latest main into [%CURRENT_BRANCH%]? [Y/N] (Default=N): "
if /i "%MERGE_CHOICE%"=="Y" (
    echo Merging origin/main into [%CURRENT_BRANCH%]...
    git merge origin/main --no-edit
) else (
    echo Skipped merge. Your branch [%CURRENT_BRANCH%] remains untouched!
)

:DONE
echo.
echo ==============================================================================
echo   All done! Press any key to close this window.
echo ==============================================================================
pause > nul
