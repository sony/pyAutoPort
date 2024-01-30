#! /bin/bash

# Reinstall local package
echo "[Installing local package]"
pip uninstall -y pyautoport
pip install .

echo "[Testing start daemon]"
session_start &
sleep 3
echo "### CONFIRM session_start seesion ###"
pgrep -ax session_start

echo "[Testing adb open and send]"
connect adb
send 'ls'
sleep 0.5
disconnect adb
echo "### CONFIRM adb seesion not exists ###"
pgrep -ax adb

echo "[Testing double open and send]"
connect adb
connect adb
send 'ls'
sleep 0.5
echo "### CONFIRM has only one adb seesion ###"
pgrep -ax adb

echo "[Testing switch session]"
connect adb
send 'ls'
sleep 0.5
connect uart
echo "### CONFIRM current session is uart ###"
send 'ls'
sleep 0.5

echo "[Testing log display]"
connect adb
set_timestamp
send 'ls'
sleep 0.5
logstart test.log
sleep 1
echo "### CONFIRM saving log file exists ###"
send 'pwd'
sleep 0.5
ls -al test.log

echo "[Cleaning up process hopefully]"
session_stop
sleep 3
echo "### CONFIRM if all session process exists ###"
pgrep -ax adb
pgrep -ax session_start
echo "### CONFIRM log file saving succeed ###"
cat test.log
rm test.log
