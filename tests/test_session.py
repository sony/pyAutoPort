"""
Test for TeraTerm Mode
"""

import time
import pyautoport

pyautoport.open_session_start()

pyautoport.open_conn('adb')
pyautoport.send('ls')
pyautoport.send('pwd')
pyautoport.close_conn('adb')
time.sleep(1)

pyautoport.open_conn('tty')
pyautoport.send('ls')
pyautoport.send('pwd')
pyautoport.close_conn('tty')
time.sleep(1)

pyautoport.session_stop()
