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
echo ### CONFIRM session_start seesion ###
tasklist| findstr /i %process_name_start%

echo [Testing adb open and send]
connect adb
send ls
disconnect adb
powershell -Command "sleep -m 3000"
echo ### CONFIRM adb seesion not exists ###
tasklist| findstr /i %process_name_adb%

echo [Testing double open and send]
connect adb
connect adb
connect adb
send ls
powershell -Command "sleep -m 3000"
echo ### CONFIRM has only one adb seesion ###
tasklist| findstr /i %process_name_adb%

echo [Testing switch session]
connect adb
send ls
connect uart
mpause 1000
echo ### CONFIRM current session is uart ###
send ls

echo [Testing log display]
connect adb
set_timestamp
send ls
echo ### COMFIRM it takes 2sec to send log ###
mpause 2000
send ls
set_timeout 2
send "ping 127.0.0.1 -c 10"
echo ### COMFIRM check waitln succeed ###
waitln bytes

echo [Testing saving log]
logstart test.log
send pwd
logwrite ">>> log stop"
logstop
powershell -Command "sleep -m 1000"
echo ### CONFIRM saving log file exists ###
dir| findstr /i  test.log

echo [Cleaning up process hopefully]
session_stop
powershell -Command "sleep -m 3000"
echo ### CONFIRM if all session process exists ###
tasklist| findstr /i %process_name_adb%
powershell -Command "sleep -m 3000"
tasklist| findstr /i %process_name_start%

pause
