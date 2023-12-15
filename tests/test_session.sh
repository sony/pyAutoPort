#! /bin/bash

# Reinstall local package
echo "[Installing local package]"
pip uninstall -y pyautoport
pip install .

echo "[Testing start daemon]"
start_daemon &
sleep 3
echo "### CONFIRM start_daemon seesion ###"
pgrep -ax start_daemon

echo "[Testing adb open and send]"
adb_connect
send 'ls'
sleep 0.5
adb_disconnect
echo "### CONFIRM adb seesion not exists ###"
pgrep -ax adb

echo "[Testing double open and send]"
adb_connect
adb_connect
send 'ls'
sleep 0.5
echo "### CONFIRM has only one adb seesion ###"
pgrep -ax adb

echo "[Testing switch session]"
adb_connect
send 'ls'
sleep 0.5
uart_connect
echo "### CONFIRM current session is uart ###"
send 'ls'
sleep 0.5

echo "[Testing log display]"
adb_connect
set_timestamp
send 'ls'
sleep 0.5
set_log test.log
sleep 1
echo "### CONFIRM saving log file exists ###"
send 'pwd'
sleep 0.5
ls -al test.log

echo "[Cleaning up process hopefully]"
stop_daemon
sleep 3
echo "### CONFIRM if all session process exists ###"
pgrep -ax adb
pgrep -ax start_daemon
echo "### CONFIRM log file saving succeed ###"
cat test.log
rm test.log
