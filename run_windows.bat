@echo off
SETLOCAL EnableDelayedExpansion
chcp 65001 > NUL

set PIPENV_VENV_IN_PROJECT=1

set PATH=%PATH%;.\bin

ffmpeg -version > NUL 2>&1
if %ERRORLEVEL% neq 0 (
    echo Cannot find ffmpeg executable, make sure it is installed and added to your PATH.
    echo You can also provide it in a folder named bin.
    pause
    exit /B 0
)

git --version > NUL 2>&1
if %ERRORLEVEL% neq 0 (
    echo Cannot find Git executable, make sure it is installed and added to your PATH.
    pause
    exit /B 0
)

python --version > NUL 2>&1
if %ERRORLEVEL% neq 0 (
    echo Cannot find Python executable, make sure it is installed and added to your PATH.
    pause
    exit /B 0
)

python -c "import pipenv" > NUL 2>&1
if %ERRORLEVEL% neq 0 (
    python -m pip install --user pipenv
)

pipenv --version > NUL 2>&1
if %ERRORLEVEL% neq 0 (
    echo Adding pipenv to PATH...
    for /F %%p IN ('python -m site --user-site') do set path_pipenv=%%p
    set PATH=!PATH!;!path_pipenv:site-packages=Scripts!
)

if not exist ".venv" ( pipenv --bare install ) else ( pipenv --bare update )

pipenv run python3 -c "exit(__import__('discord').opus.is_loaded())" > NUL 2>&1
if %ERRORLEVEL% equ 0 (
    echo Cannot find libopus on your system, make sure it is installed.
    pause
    exit /B 0
)

del /Q panda.log
pipenv run python panda.py
pause