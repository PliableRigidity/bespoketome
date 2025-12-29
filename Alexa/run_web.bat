@echo off
echo ================================================
echo JARVIS - Particle Sphere Visualization
echo ================================================
echo.
echo Starting server...
echo Access the sphere UI at: http://localhost:5000/sphere
echo Access the demo at: http://localhost:5000/sphere/demo
echo Access the chat UI at: http://localhost:5000/
echo.
echo Press Ctrl+C to stop the server
echo ================================================
echo.

cd /d "%~dp0"
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)
python web_server.py
pause
