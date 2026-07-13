@echo off
REM Launches Chrome with remote debugging enabled, using a dedicated
REM profile folder so it doesn't collide with your normal Chrome windows.
REM Log into Amazon, Keepa, and Jungle Scout in THIS window once --
REM the script will reuse that session on every run.

set CHROME_PATH="C:\Program Files\Google\Chrome\Application\chrome.exe"
set DEBUG_PORT=9222
set PROFILE_DIR=%USERPROFILE%\chrome-fba-debug-profile

if not exist %CHROME_PATH% (
    set CHROME_PATH="C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
)

start "" %CHROME_PATH% --remote-debugging-port=%DEBUG_PORT% --user-data-dir="%PROFILE_DIR%"
