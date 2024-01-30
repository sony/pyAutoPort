import pyautoport
import time

pyautoport.connect_adb_via_bash()
pyautoport.send('ls')
pyautoport.send('pwd')
pyautoport.disconnect_adb_via_bash()
time.sleep(1)

pyautoport.connect_uart_via_bash()
pyautoport.send('ls')
pyautoport.send('pwd')
pyautoport.disconnect_uart_via_bash()
time.sleep(1)

pyautoport.stop_via_bash()
