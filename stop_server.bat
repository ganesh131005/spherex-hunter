@echo off
setlocal
cd /d "%~dp0"
title Stop SPHEREx Hunter Server
color 0C

echo ==============================================================================
echo            STOPPING SPHEREx HUNTER BACKEND (PORT 8000)
echo ==============================================================================
echo.

set FOUND=0
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    set FOUND=1
    echo Terminating server process PID: %%a ...
    taskkill /F /PID %%a >nul 2>&1
)

if %FOUND%==1 (
    echo.
    echo [OK] SPHEREx Hunter server stopped successfully. Port 8000 is now free.
) else (
    echo.
    echo [INFO] No server was running on port 8000.
)

echo.
pause
