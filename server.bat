@echo off


echo 'Y' to run server, 'T' for testing, 'set' to activate env.
set /p userInput=Please enter your choice (Y/T/set): 

:: Check user input and act accordingly
if /I "%userInput%"=="Y" (
    cd C:\Coding\Projects\Server\.venv\Scripts
    call activate.bat
    cd C:\Coding\Projects\Server
    set FLASK_APP=run:get_app
    set FLASK_RUN_PORT=5000
    set FLASK_RUN_HOST=0.0.0.0
    echo Running Flask server...
    flask --debug run

) else if /I "%userInput%"=="T" (
    cd C:\Coding\Projects\Server\.venv\Scripts
    call activate.bat
    cd C:\Coding\Projects\Server
    set FLASK_APP=run:get_app
    set FLASK_RUN_PORT=5000
    set FLASK_RUN_HOST=0.0.0.0
    set FLASK_ENV=deploy
    echo Running Flask server...
    flask run

) else if /I "%userInput%"=="set" (
    cd C:\Coding\Projects\Server\.venv\Scripts
    call activate.bat
    cd C:\Coding\Projects\Server
    set FLASK_APP=run:get_app
    echo APP has been set

) else (
    :: Handle invalid input
    echo Invalid input. Please enter Y or N.
)

