#! /bin/bash

# Reinstall local package
echo "[Installing local package]"
pip uninstall -y pyautoport
pip install .

echo "[Testing open and send]"
adb_open&
adb_send 'ls /'
adb_close
sleep 3
pgrep -ax adb

echo "[Testing double open]"
adb_open&
sleep 3
adb_open&
sleep 3
echo "CONFIRM if already opened warning is shown"
pgrep -ax adb

echo "[Testing reopen]"
adb_reopen&
sleep 3
echo "CONFIRM if adb session is opened"
PID=$!
adb_send 'ls /'
sleep 3

echo "[Testing force killing]"
kill $PID
sleep 2
pgrep -ax adb
echo "CONFIRM if adb_reopen process exists"

echo "[Cleaning up process hopefully]"
adb_reopen&
sleep 2
adb_close
pgrep -ax adb
