import pyautoport

pyautoport.adb_open()
pyautoport.adb_send('ls /')
pyautoport.adb_close()
