import pyautoport
import time

pyautoport.adb_connect_via_bash()
pyautoport.send('ls')
pyautoport.send('pwd')
pyautoport.adb_disconnect_via_bash()
time.sleep(1)

pyautoport.uart_connect_via_bash()
pyautoport.send('ls')
pyautoport.send('pwd')
pyautoport.uart_disconnect_via_bash()
time.sleep(1)

pyautoport.stop_via_bash()
