@echo off
echo YouTube Marketing Expert Agent
echo ==============================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

echo Python detected: 
python --version

REM Check if virtual environment exists
if not exist "venv" (
    echo.
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if requirements are installed
if not exist "venv\Lib\site-packages\streamlit" (
    echo.
    echo Installing requirements...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install requirements
        pause
        exit /b 1
    )
)

REM Check if .env file exists and is configured
if not exist ".env" (
    echo.
    echo ERROR: .env file not found
    echo Please run configure.py first to set up your API credentials
    echo.
    python configure.py
    pause
    exit /b 1
)

REM Run the application
echo.
echo Starting YouTube Marketing Expert Agent...
echo.
echo The application will open in your default web browser
echo Press Ctrl+C to stop the application
echo.
streamlit run main.py

pause
