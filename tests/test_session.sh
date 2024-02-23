#! /bin/bash

# Reinstall local package
echo "[Installing local package]"
pip uninstall -y pyautoport
pip install .

echo "[Testing start daemon]"
session_start &
echo "### CONFIRM session_start seesion ###"
pgrep -ax session_start

sleep 1
echo "[Testing adb open and send]"
connect adb
send 'ls'
disconnect adb
echo "### CONFIRM adb seesion not exists ###"
sleep 0.5
pgrep -ax adb

sleep 1
echo "[Testing double open and send]"
connect adb
connect adb
send 'ls'
echo "### CONFIRM has only one adb seesion ###"
sleep 0.5
pgrep -ax adb

sleep 1
echo "[Testing switch session]"
connect adb
send 'ls'
echo "### CONFIRM current session is uart ###"
connect uart
send 'ls'

sleep 1
echo "[Testing log display]"
connect adb
set_timestamp
send 'ls'
echo "### COMFIRM it takes 2sec to send log ###"
mpause 2000
send 'ls'

sleep 3
echo "[Testing saving log]"
logstart test.log
send 'pwd'
echo "### CONFIRM saving log file exists ###"
sleep 1
ls -al test.log

sleep 1
echo "[Cleaning up process hopefully]"
session_stop
echo "### CONFIRM if all session process exists ###"
pgrep -ax adb
pgrep -ax session_start
echo "### CONFIRM log file saving succeed ###"
sleep 0.5
cat test.log
rm test.log
