@echo off


echo Y to run server, N to see settings, set to activate env.
set /p userInput=Please enter your choice (Y/N/set): 

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

) else if /I "%userInput%"=="N" (
    cd C:\Coding\Projects\Server
    echo FLASK_APP=run:get_app
    echo FLASK_RUN_PORT=%FLASK_RUN_PORT%
    echo FLASK_RUN_HOST=%FLASK_RUN_HOST%
    echo flask --debug run

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

