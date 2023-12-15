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
import socket, select
import argparse
from pyautoport.Connection import Connection

PORT_WRITE = 18890
class_session = None
pid_file = 'tester-daemon.pid'

def start_daemon():
    global class_session
    class_session = Connection()
    with open(pid_file, 'w') as f:
        f.write(f'{os.getpid()}\n')

    # Set daemon socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('localhost', PORT_WRITE))
    server_socket.listen(5)
    print(f'Server listening on port {PORT_WRITE}')

    while class_session is not None:
        client_socket, address = server_socket.accept()
        # Receive data from the client
        ready = select.select([client_socket], [], [], 0.25)
        while ready[0]:
            data = client_socket.recv(1024).decode().strip()
            ready = select.select([client_socket], [], [], 0.25)
            if len(data) > 2 and data[0:2] == 'it':
                data_index = data.find('@')
                data_function = data[2:data_index]
                if data_function == 'adb_connect':
                    adb_connect()
                if data_function == 'adb_disconnect':
                    close('adb')
                if data_function == 'uart_connect':
                    uart_connect()
                if data_function == 'uart_disconnect':
                    close('tty')
                if data_function == 'stop':
                    if check_connection():
                        close('all')
                    client_socket.send('Stop listening\n'.encode())
                    client_socket.close()
                    print(f'Server listening stop')
                    return
                if data_function == 'send':
                    if check_connection():
                        send(data[data_index+1:])
                if data_function == 'save':
                    if check_connection():
                        set_log(data[data_index+1:])
                if data_function == 'set_timestamp':
                    if check_connection():
                        set_timestamp()

def check_connection():
    global class_session
    if class_session.type is None or class_session.connect_check() is None:
        print('Did you run adb_connect or uart_connect')
        return False
    return True

def open_class_daemon_on_demand():
    if not os.path.exists(pid_file):
        start_thread = threading.Thread(target=start_daemon)
        start_thread.start()
        time.sleep(0.5)

def uart_connect():
    global class_session
    class_session.type = 'tty'
    if class_session.connect_check() is None:
        port = os.environ.get('TESTER_UART_PORT', '/dev/ttyACM0')
        baudrate = os.environ.get('TESTER_UART_BAUDRATE', '125000')
        class_session.connect(port=port, baudrate=baudrate)

def adb_connect():
    global class_session
    class_session.type = 'adb'
    if class_session.connect_check() is None:
        serial_port = os.environ.get('TESTER_ADB_PORT', '')
        class_session.connect(serial_port=serial_port)

def close(port):
    global start_thread
    global class_session
    if port == 'all' or port == 'tty':
        class_session.type = 'tty'
        class_session.disconnect()
        class_session.type = 'adb'
    if port == 'all' or port == 'adb':
        class_session.type = 'adb'
        class_session.disconnect()
        class_session.type = 'tty'
    if port == 'all':
        class_session = None
#        os.killpg(os.getpid(), signal.SIGTERM)

def send(text):
    global class_session
    class_session.send_data(text)
    time.sleep(0.5)

def set_log(file_name):
    global class_session
    class_session.set_log(file_name)
    time.sleep(0.5)

def set_timestamp():
    global class_session
    class_session.set_timestamp()
    time.sleep(0.5)

def send_via_bash():
    parser = argparse.ArgumentParser()
    parser.add_argument('text', nargs='+', help='Text to send via Terminal')
    parser.add_argument('-t', '--timeout', type=float, help='Time to wait before stop reading')
    args = parser.parse_args()
    text = ' '.join(args.text)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(('localhost', PORT_WRITE))
    except ConnectionRefusedError:
        print('Did you run start_daemon &')

    client_socket.send(f'itsend@{text}\n'.encode())
    time.sleep(0.5)

def set_log_via_bash():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='+', help='Save log')
    args = parser.parse_args()
    file_name = ' '.join(args.file)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(('localhost', PORT_WRITE))
    except ConnectionRefusedError:
        print('Did you run start_daemon &')

    client_socket.send(f'itsave@{file_name}\n'.encode())
    time.sleep(0.5)

def set_timestamp_via_bash():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(('localhost', PORT_WRITE))
    except ConnectionRefusedError:
        print('Did you run start_daemon &')

    client_socket.send(f'itset_timestamp@\n'.encode())
    time.sleep(0.5)

def adb_connect_via_bash():
    open_class_daemon_on_demand()
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', PORT_WRITE))
    client_socket.send(f'itadb_connect@\n'.encode())
    time.sleep(0.5)

def adb_disconnect_via_bash():
    open_class_daemon_on_demand()
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(('localhost', PORT_WRITE))
    except ConnectionRefusedError:
        print('Did you run start_daemon &')
    client_socket.send(f'itadb_disconnect@\n'.encode())
    time.sleep(0.5)

def uart_connect_via_bash():
    open_class_daemon_on_demand()
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', PORT_WRITE))
    client_socket.send(f'ituart_connect@\n'.encode())
    time.sleep(0.5)

def uart_disconnect_via_bash():
    open_class_daemon_on_demand()
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(('localhost', PORT_WRITE))
    except ConnectionRefusedError:
        print('Did you run start_daemon &')
    client_socket.send(f'ituart_disconnect@\n'.encode())
    time.sleep(0.5)

def stop_via_bash():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(('localhost', PORT_WRITE))
    except ConnectionRefusedError:
        print('Did you run start_daemon &')

    client_socket.send(f'itstop@\n'.encode())
    time.sleep(0.5)
    client_socket.close()
    os.remove(pid_file)
