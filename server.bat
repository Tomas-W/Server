@echo off

echo 'Y' to run in debug mode, 'D' for deployment, 'set' to activate env.
set /p userInput=Please enter your choice (Y/D/set): 

:: Check user input and act accordingly
if /I "%userInput%"=="Y" (
    cd C:\Coding\Projects\Server\.venv\Scripts
    call activate.bat
    cd C:\Coding\Projects\Server
    set FLASK_APP=run:get_app
    set FLASK_ENV=debug
    set PORT=5000
    echo Running Flask server in debug mode on port %PORT%...
    python run.py

) else if /I "%userInput%"=="D" (
    cd C:\Coding\Projects\Server\.venv\Scripts
    call activate.bat
    cd C:\Coding\Projects\Server
    set FLASK_APP=run:get_app
    set FLASK_ENV=deploy
    set PORT=8080
    echo Running Flask server in deployment mode with SSL on port %PORT%...
    :: Note: Running on port 443 might require administrator privileges
    python run.py

) else if /I "%userInput%"=="set" (
    cd C:\Coding\Projects\Server\.venv\Scripts
    call activate.bat
    cd C:\Coding\Projects\Server
    set FLASK_APP=run:get_app
    set FLASK_ENV=debug
    echo APP has been set

) else (
    :: Handle invalid input
    echo Invalid input. Please enter Y, D, or set.
)

