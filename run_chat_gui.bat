@echo off
cd /d %~dp0

setlocal
set PYTHONPATH=%CD%\src;%PYTHONPATH%

echo [START] %date% %time% > logs.txt
python chat_gui.py >> logs.txt 2>&1
echo [END] %date% %time% >> logs.txt

endlocal
pause
