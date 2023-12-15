@echo off

set process_name_adb=adb
set process_name_start=start_daemon

REM Reinstall local package
echo [Installing local package]
pip uninstall -y pyautoport
pip install .

echo [Testing start daemon]
start /B start_daemon
REM timeout /T 1 /NOBREAK
powershell -Command "sleep -m 1000"
echo ### CONFIRM start_daemon seesion ###
tasklist| findstr /i %process_name_start%

echo [Testing adb open and send]
adb_connect
send ls
adb_disconnect
powershell -Command "sleep -m 1000"
echo ### CONFIRM adb seesion not exists ###
tasklist| findstr /i %process_name_adb%

echo [Testing double open and send]
adb_connect
adb_connect
adb_connect
send ls
echo ### CONFIRM has only one adb seesion ###
tasklist| findstr /i %process_name_adb%

echo [Testing switch session]
adb_connect
send ls
powershell -Command "sleep -m 500"
echo ### CONFIRM current session is uart ###
uart_connect
send ls
powershell -Command "sleep -m 500"

echo [Testing log display]
adb_connect
set_timestamp
send ls
set_log test.log
powershell -Command "sleep -m 1000"
echo ### CONFIRM saving log file exists ###
send pwd
dir| findstr /i  test.log

echo [Cleaning up process hopefully]
stop_daemon
powershell -Command "sleep -m 1000"
echo ### CONFIRM if all session process exists ###
tasklist| findstr /i %process_name_adb%
tasklist| findstr /i %process_name_start%


pause
