@echo off
echo ========================================
echo ArcGIS AI Assistant
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found!
    echo Please run setup.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if Ollama is running
echo Checking Ollama connection...
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: Ollama is not running!
    echo Please start Ollama before running this application.
    echo.
    echo To start Ollama, run: ollama serve
    echo.
    pause
    exit /b 1
)

echo Ollama is running!
echo.

REM Start the application
echo Starting ArcGIS AI Assistant...
echo.
streamlit run app.py

REM Deactivate virtual environment on exit
deactivate

