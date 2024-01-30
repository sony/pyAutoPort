# Copyright 2023 Sony Corporation
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import os, subprocess, time
import threading, signal
import serial
import serial.tools.list_ports
from pyautoport.addon.addon import AddonStrategy

class TTYStrategy(AddonStrategy):
    _instance = None
    _first_init = True
    port = None
    timestamp = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TTYStrategy, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._first_init:
            self.timeout = 0.5
            self.log_file = 'tty.log'
            self.log = None
            self.save_log = False
            self.thread = None
            self.running = False
            TTYStrategy._first_init = False

    def _start_thread(self):
        self.running = True
        self.log = open(self.log_file, 'w', encoding='utf-8', errors='ignore')
        self.thread = threading.Thread(target=self._read)
        self.thread.start()

    def _stop_thread(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)

    def set_timeout(self, timeout):
        self.timeout = timeout

    def set_log(self, log_file):
        if os.path.exists(self.log_file):
            if self.log:
                self.log.close()
            os.remove(self.log_file)
        self.log_file = log_file
        self.save_log = True
        if self.port:
            port = os.environ.get('TESTER_UART_PORT', '/dev/ttyACM0')
            baudrate = os.environ.get('TESTER_UART_BAUDRATE', '125000')
            self.connect(port=port, baudrate=baudrate)

    def connect(self, port='/dev/ttyACM0', baudrate=125000):
        if self.port:
            self.disconnect()
            time.sleep(0.3)
        self._start_thread()
        try:
            self.port = serial.Serial(port=port, baudrate=baudrate, timeout=self.timeout)
        except:
            self.disconnect()
            print('connect_uart failed, Please make sure to set the correct {TESTER_UART_PORT} and {TESTER_UART_BAUDRATE}')
            print('COM list:')
            for port in list(serial.tools.list_ports.comports()):
                print(f'{port.device}: {port.description}')

    def send_data(self, data):
        self.port.write(data.encode('utf-8'))
        self.port.write('\n'.encode('utf-8'))
        time.sleep(0.05)

    def _read(self):
        has_message = False
        while self.running:
            output = ''
            if self.port:
                output = self.port.readline().decode(encoding='utf-8', errors='ignore')
            if not self.running:
                break
            if output:
                #output = output.strip()
                if self.timestamp and has_message:
                    time_stamp = time.time()
                    output = '[' + str(time_stamp) + '] ' + output
                if has_message:
                    print(output.strip())
                self.log.write(output.replace('\r\n', '\n').replace('\r', ''))
                self.log.flush()
                has_message = True
            else:
                has_message = False
                time.sleep(0.1)

    def disconnect(self):
        if self.running:
            self._stop_thread()
        if not self.save_log and os.path.exists(self.log_file):
            if self.log:
                self.log.close()
            os.remove(self.log_file)
        if self.port:
            self.port.close()
            self.port = None
