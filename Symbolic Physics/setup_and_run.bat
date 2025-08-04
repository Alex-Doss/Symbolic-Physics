@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo === Symbolic Physics v0.4 Full Pipeline with AutoTest ===

where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install Python 3.10+.
    pause
    exit /b 1
)

if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
)

call "venv\Scripts\activate.bat"

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing dependencies...
pip install -r requirements.txt

echo Running AutoTest sequence...
python main_gui.py

pause
