@echo off

set process_name_adb=adb
set process_name_start=session_start

REM Reinstall local package
echo [Installing local package]
pip uninstall -y pyautoport
pip install .

echo [Testing start daemon]
start /B session_start
REM timeout /T 1 /NOBREAK
powershell -Command "sleep -m 1000"
echo ### CONFIRM session_start seesion ###
tasklist| findstr /i %process_name_start%

echo [Testing adb open and send]
connect adb
send ls
disconnect adb
powershell -Command "sleep -m 1000"
echo ### CONFIRM adb seesion not exists ###
tasklist| findstr /i %process_name_adb%

echo [Testing double open and send]
connect adb
connect adb
connect adb
send ls
echo ### CONFIRM has only one adb seesion ###
tasklist| findstr /i %process_name_adb%

echo [Testing switch session]
connect adb
send ls
powershell -Command "sleep -m 500"
echo ### CONFIRM current session is uart ###
connect uart
send ls
powershell -Command "sleep -m 500"

echo [Testing log display]
connect adb
set_timestamp
send ls
logstart test.log
powershell -Command "sleep -m 1000"
echo ### CONFIRM saving log file exists ###
send pwd
dir| findstr /i  test.log

echo [Cleaning up process hopefully]
session_stop
powershell -Command "sleep -m 1000"
echo ### CONFIRM if all session process exists ###
tasklist| findstr /i %process_name_adb%
tasklist| findstr /i %process_name_start%

pause
