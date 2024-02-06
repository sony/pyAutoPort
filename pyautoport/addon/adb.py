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

"""
TeraTrem Mode - ADB Connect
"""

import os
import subprocess
import time
import threading
import signal
from queue import Queue
from pyautoport.addon.addon import AddonStrategy

# pylint: disable=duplicate-code
class ADBStrategy(AddonStrategy):
    """ Connection via adb """
    log_file = 'adb.log'
    save_log = False
    data = Queue()
    adb_event = threading.Event()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ADBStrategy, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._first_init:
            self.timeout = 1
            self.thread = None
            self.running = False
            self.cmd = 'adb shell'
            ADBStrategy._first_init = False

    def _start_thread(self):
        self.running = True
        self.adb_event.clear()
        self.thread = threading.Thread(target=self._create_process)
        self.thread.daemon = True
        self.thread.start()

    def _stop_thread(self):
        self.running = False
        while self.adb_event.is_set():
            time.sleep(0.1)
        if self.thread:
            self.thread.join(timeout=1)

    def _create_process(self):
        self.adb_event.set()
        if os.name == 'posix':
            with subprocess.Popen(
                    self.cmd,
                    shell=True,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    start_new_session=True
            ) as port:
                self._read_and_write(port)
                os.killpg(os.getpgid(port.pid), signal.SIGTERM)
        if os.name == 'nt':
            with subprocess.Popen(
                    self.cmd,
                    shell=False,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE
            ) as port:
                self._read_and_write(port)
                subprocess.run(
                        ['taskkill', '/T', '/F', '/PID', str(port.pid)],
                        timeout=2,
                        check=False
                    )
        self.adb_event.clear()

    def _read_and_write(self, port):
        read_thread = threading.Thread(target=self._read, args=(port,))
        read_thread.daemon = True
        read_thread.start()
        self._write(port)
        read_thread.join(timeout=1)

    def _write(self, port):
        while self.running:
            while self.data.qsize() > 0:
                write_data = self.data.get()
                if port.stdin.closed:
                    print('process of [adb shell] was exited\n')
                    self.running = False
                    break
                port.stdin.write(write_data)
                port.stdin.flush()

    def _read(self, port):
        has_message = False
        with open(self.log_file, 'a', encoding='utf-8', errors='ignore') as f:
            while self.running:
                read_data = ''
                if port.stdout.closed:
                    print('process of [adb shell] was exited\n')
                    self.running = False
                    break
                read_data = port.stdout.readline().decode(encoding='utf-8', errors='ignore')
                if read_data:
                    if self.timestamp and has_message:
                        time_stamp = time.time()
                        read_data = '[' + str(time_stamp) + '] ' + read_data
                    if has_message:
                        print(read_data.strip())
                    f.write(read_data.replace('\r\n', '\n').replace('\r', ''))
                    f.flush()
                    has_message = True
                else:
                    has_message = False
                    time.sleep(0.1)

    def set_timeout(self, timeout):
        """ set timeout in adb session """
        self.timeout = timeout

    def set_log(self, log_file):
        """ set logstart in adb session """
        if self.running:
            self.disconnect()
            serial_port = os.environ.get('TESTER_ADB_PORT', '')
        self.log_file = log_file
        self.save_log = True
        self.connect(serial_port=serial_port)
        with open(self.log_file, 'w', encoding='utf-8', errors='ignore') as f:
            f.write(f'>>>>>>>>>> adb log start, port={serial_port}\n')

    def connect(self, serial_port=''):
        """ connect via adb """
        if self.running:
            self.disconnect()
        if serial_port != '':
            self.cmd = 'adb -s ' + str(serial_port) + ' shell'
        self._start_thread()

    def send_data(self, data):
        """ send commands via adb session """
        if self.adb_event.is_set():
            self.data.put(data.encode('utf-8'))
            self.data.put('\n'.encode('utf-8'))
            time.sleep(0.05)
        else:
            print('connect_adb failed,'
                'Please make sure execute connect adb before')

    def disconnect(self):
        """ disconnect from adb """
        if self.running:
            self._stop_thread()
            time.sleep(0.3)
        if not self.save_log and os.path.exists(self.log_file):
            time.sleep(0.3)
            os.remove(self.log_file)
