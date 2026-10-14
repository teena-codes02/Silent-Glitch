@echo off
title SILENT GLITCH - Haunted Castle Edition
echo ========================================================
echo    SILENT GLITCH: HAUNTED CASTLE EDITION
echo    8 Haunted Rooms ^| Graphical Gothic Doors ^| 3 Lives
echo ========================================================
echo.
echo Launching game...
py -3.13 main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Trying fallback Python launcher...
    py main.py
    if %ERRORLEVEL% NEQ 0 (
        python main.py
    )
)
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo If Pygame is not installed, install it with:
    echo   py -m pip install pygame
    echo.
    pause
)
