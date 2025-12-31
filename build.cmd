@echo off
setlocal

:: Define paths
set SOURCE_DIR=%~dp0
set DIST_DIR=%~dp0dist
set KEY_FILE=%~dp0key.pem

:: Ensure dist directory exists
if not exist "%DIST_DIR%" mkdir "%DIST_DIR%"

:: Run the python pack script
:: The script now handles timestamping automatically
python "%~dp0pack_crx.py" "%~dp0." "%DIST_DIR%\wikilink-helper-1.3.0.crx" --key "%KEY_FILE%"

if %ERRORLEVEL% EQU 0 (
    echo Build successful!
) else (
    echo Build failed with error code %ERRORLEVEL%
)

endlocal
pause
