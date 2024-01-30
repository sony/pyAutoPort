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
from pyautoport.addon.addon import AddonStrategy

class ADBStrategy(AddonStrategy):
    _instance = None
    _first_init = True
    port = None
    timestamp = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ADBStrategy, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._first_init:
            self.timeout = 1
            self.log_file = 'adb.log'
            self.log = None
            self.save_log = False
            self.thread = None
            self.running = False
            ADBStrategy._first_init = False

    def _start_thread(self):
        self.running = True
        self.log = open(self.log_file, 'w', encoding='utf-8', errors='ignore')
        self.thread = threading.Thread(target=self._read)
        self.thread.setDaemon(True)
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
            serial_port = os.environ.get('TESTER_ADB_PORT', '')
            self.connect(serial_port=serial_port)

    def connect(self, serial_port=''):
        if self.port:
            self.disconnect()
            time.sleep(0.3)
        self._start_thread()
        if serial_port != '':
            cmd = 'adb -s ' + str(serial_port) + ' shell'
        else:
            cmd = 'adb shell'
        if os.name == 'posix':
            self.port = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, preexec_fn=os.setsid)
            os.set_blocking(self.port.stdout.fileno(), False)
        if os.name == 'nt':
            self.port = subprocess.Popen(cmd, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
#        os.set_blocking(self.port.stdout.fileno(), False)

    def send_data(self, data):
        self.port.stdin.write(data.encode('utf-8'))
        self.port.stdin.write('\n'.encode('utf-8'))
        self.port.stdin.flush()

    def _read(self):
        has_message = False
        while self.running:
            output = ''
            if self.port:
                output = self.port.stdout.readline().decode(encoding='utf-8', errors='ignore')
                if self.port is None or self.port.poll() is not None:
                    print('process of [adb shell] was exited\n')
                    self.port = None
                    break
            if not self.running:
                break
            if output:
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
            if os.name == 'posix':
                self.port.terminate()
                self.port.wait()
                os.killpg(self.port.pid, signal.SIGTERM)
            if os.name == 'nt':
                subprocess.run(
                        ['taskkill', '/T', '/F', '/PID', str(self.port.pid)],
                        timeout=2
                    )
            self.port = None
