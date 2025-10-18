@echo off
echo ========================================
echo ArcGIS AI Assistant - Setup
echo ========================================
echo.

REM Check Python installation
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.11 or higher from python.org
    pause
    exit /b 1
)

python --version
echo.

REM Create virtual environment
if exist "venv" (
    echo Virtual environment already exists.
    choice /C YN /M "Do you want to recreate it"
    if errorlevel 2 goto :skip_venv
    echo Removing old virtual environment...
    rmdir /s /q venv
)

echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment!
    pause
    exit /b 1
)

:skip_venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo.
echo Installing dependencies...
echo This may take several minutes...
echo.
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo.
    echo Creating .env file from template...
    copy .env.example .env
    echo.
    echo IMPORTANT: Please edit .env file with your ArcGIS credentials!
    echo.
)

REM Check Ollama installation
echo.
echo Checking Ollama installation...
ollama --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: Ollama is not installed!
    echo Please install Ollama from https://ollama.ai/
    echo.
) else (
    ollama --version
    echo.
    echo Checking if Qwen2 model is installed...
    ollama list | findstr "qwen2" >nul 2>&1
    if errorlevel 1 (
        echo.
        echo Qwen2 model not found. Pulling model...
        echo This may take several minutes depending on your internet connection...
        ollama pull qwen2.5:1.5b
    ) else (
        echo Qwen2 model is already installed!
    )
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env file with your ArcGIS credentials (optional)
echo 2. Make sure Ollama is running: ollama serve
echo 3. Run the application: run.bat
echo.
pause

