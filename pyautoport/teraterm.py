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
TeraTerm Mode
"""

import os
import time
import threading
import socket
import select
import argparse
from queue import Queue
from pyautoport.session import ConnectSession

PORT_WRITE = 18890
PID_FILE = 'tester-daemon.pid'
event_stop_session = threading.Event()

def session_start():
    """ Open a session thread """
    session = ConnectSession()
    queue_recv = Queue()
    event_stop_session.clear()
    with open(PID_FILE, 'w', encoding='utf-8') as f:
        f.write(f'{os.getpid()}\n')

    # Set daemon socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('localhost', PORT_WRITE))
    server_socket.listen(5)
    print(f'Server listening on port {PORT_WRITE}')

    recv_thread = threading.Thread(target=recv_handle, args=(session, queue_recv,))
    recv_thread.start()

    while session is not None:
        client_socket, _ = server_socket.accept()
        ready = select.select([client_socket], [], [], 0.25)
        while ready[0]:
            ready = select.select([client_socket], [], [], 0.25)
            data = client_socket.recv(1024).decode().strip()
            if len(data) > 2 and data[0:2] == 'it':
                queue_recv.put(data)
            if len(data) > 6 and data[0:6] == 'itstop':
                while not event_stop_session.is_set():
                    time.sleep(0.1)
                client_socket.send('Stop listening\n'.encode())
                client_socket.close()
                return

def recv_handle(session, queue_recv):
    """ receive commands handle """
    while session is not None:
        if queue_recv.qsize() > 0:
            data = queue_recv.get()
            data_index = data.find('@')
            data_function = data[2:data_index]
            if data_function == 'connect':
                open_conn(session, data[data_index+1:])
            if data_function == 'disconnect':
                close_conn(session, data[data_index+1:])
            if data_function == 'stop':
                close_conn(session, 'all')
                print('Server listening stop')
                event_stop_session.set()
                break
            if data_function == 'send' and check_connection(session):
                send(session, data[data_index+1:])
            if data_function == 'save' and check_connection(session):
                set_log(session, data[data_index+1:])
            if data_function == 'set_timestamp' and check_connection(session):
                set_timestamp(session)
            time.sleep(0.3)

def check_connection(session):
    """ Check session connect status """
    if session.type is None or session.connect_check() is False:
        print('Did you run connect_adb or connect_uart')
        return False
    return True

def open_session_start():
    """ Python or Bash entry for start session"""
    if not os.path.exists(PID_FILE):
        start_thread = threading.Thread(target=session_start)
        start_thread.start()

def open_conn(session, port):
    """ session connect """
    first_connect = True
    if port in ('adb', 'tty'):
        session.type = port
        if session.connect_check():
            first_connect = False
    if port == 'tty' and first_connect:
        port = os.environ.get('TESTER_UART_PORT', '/dev/ttyACM0')
        baudrate = os.environ.get('TESTER_UART_BAUDRATE', '125000')
        session.connect(port=port, baudrate=baudrate)
    if port == 'adb' and first_connect:
        serial_port = os.environ.get('TESTER_ADB_PORT', '')
        session.connect(serial_port=serial_port)
    time.sleep(0.3)

def close_conn(session, port):
    """ session disconnect """
    if port in ('all', 'tty'):
        session.type = 'tty'
        session.disconnect()
        session.type = 'adb'
    if port in ('all', 'adb'):
        session.type = 'adb'
        session.disconnect()
        session.type = 'tty'
    if port == 'all':
        session = None
    time.sleep(0.3)

def send(session, text):
    """ send text in session """
    session.send_data(text)

def set_log(session, file_name):
    """ set save log in session """
    session.set_log(file_name)
    time.sleep(0.3)

def set_timestamp(session):
    """ set timestamp in session """
    session.set_timestamp()

def connect_via_bash():
    """ Python or Bash entry for connect """
    parser = argparse.ArgumentParser()
    parser.add_argument('connection', nargs='+', help='Connect to adb or uart via Terminal')
    args = parser.parse_args()
    connection = ' '.join(args.connection)
    infos = connection.split()
    method = infos[0]

    open_session_start()
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', PORT_WRITE))
    if method == 'adb':
        client_socket.send('itconnect@adb\n'.encode())
    elif method == 'uart':
        client_socket.send('itconnect@tty\n'.encode())
    else:
        parser.print_help()
    time.sleep(0.5)

def disconnect_via_bash():
    """ Python or Bash entry for disconnect """
    parser = argparse.ArgumentParser()
    parser.add_argument('connection', nargs='+', help='Disconnect to adb or uart via Terminal')
    args = parser.parse_args()
    connection = ' '.join(args.connection)
    infos = connection.split()
    method = infos[0]

    open_session_start()
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(('localhost', PORT_WRITE))
    except ConnectionRefusedError:
        print('Did you run session_start &')
    if method == 'adb':
        client_socket.send('itdisconnect@adb\n'.encode())
    elif method == 'uart':
        client_socket.send('itdisconnect@tty\n'.encode())
    else:
        parser.print_help()
    time.sleep(0.5)

def send_via_bash():
    """ Python or Bash entry for send commands """
    parser = argparse.ArgumentParser()
    parser.add_argument('text', nargs='+', help='Text to send via Terminal')
    args = parser.parse_args()
    text = ' '.join(args.text)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(('localhost', PORT_WRITE))
    except ConnectionRefusedError:
        print('Did you run session_start &')

    client_socket.send(f'itsend@{text}\n'.encode())
    time.sleep(0.5)

def set_log_via_bash():
    """ Python or Bash entry for logstart """
    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='+', help='Save log')
    args = parser.parse_args()
    file_name = ' '.join(args.file)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(('localhost', PORT_WRITE))
    except ConnectionRefusedError:
        print('Did you run session_start &')

    client_socket.send(f'itsave@{file_name}\n'.encode())
    time.sleep(0.5)

def set_timestamp_via_bash():
    """ Python or Bash entry for set timestamp display """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(('localhost', PORT_WRITE))
    except ConnectionRefusedError:
        print('Did you run session_start &')

    client_socket.send('itset_timestamp@\n'.encode())
    time.sleep(0.5)

def session_stop():
    """ Python or Bash entry for stop session """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(('localhost', PORT_WRITE))
    except ConnectionRefusedError:
        print('Did you run session_start &')

    client_socket.send('itstop@\n'.encode())
    time.sleep(0.5)
    client_socket.close()
    os.remove(PID_FILE)
