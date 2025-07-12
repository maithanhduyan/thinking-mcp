@echo off
REM Knowledge Graph WebUI Launcher
REM Quick start script for Windows

echo.
echo ==============================================
echo   🧠 Thinking MCP - Knowledge Graph WebUI
echo ==============================================
echo.

cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo 💡 Please install Python 3.6+ and try again
    pause
    exit /b 1
)

REM Check if memory.json exists
if not exist "..\app\memory.json" (
    echo ⚠️  Warning: memory.json not found in ..\app\
    echo 💡 The WebUI will use sample data
    echo.
)

REM Start the server
echo 🚀 Starting WebUI server...
echo.
python webui_server.py

echo.
echo 👋 WebUI server stopped
pause
