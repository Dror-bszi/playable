# setup_windows.bat
@echo off

REM Create virtual environment if it doesn't exist
if not exist .venv (
    echo 🔧 Creating virtual environment and installing dependencies...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    pip install --upgrade pip
    pip install flask opencv-python mediapipe
    echo ✅ Setup complete.
) else (
    echo ✅ Environment already set up.
    echo You can now run the application using:
    echo   .venv\Scripts\activate.bat && python main.py
)

pause