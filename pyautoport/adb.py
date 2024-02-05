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
ADB Basic Mode
"""

import argparse
import subprocess
import threading
import socket
import time
import os
import select
from queue import Queue

PORT_ABD_WRITE = 18888
PORT_ADB_SET_TIMEOUT = 18889
PID_FILE = '/tmp/tester-adb-daemon.pid'
EVENT_STOP_ADB_SESSION = threading.Event()
EVENT_STOP_ADB_SESSION.clear()
QUEUE_ADB_OUTPUT = Queue()


# Daemon
def open_adb_daemon_on_demand():
    """Open thread when no thread is running"""
    if not os.path.exists(PID_FILE):
        EVENT_STOP_ADB_SESSION.clear()
        adb_daemon_thread = threading.Thread(target=start_adb_daemon)
        adb_daemon_thread.start()
    else:
        print('''
Is someone else running adb_open now?
Or did you run adb_close last time?
Run adb_reopen& instead to kill all other adb_open sessions
        ''')


def read_and_respond_until_timeout(client_socket, adb_timeout=1):
    """Send received text to client"""
    last_update = time.time()

    while time.time() - last_update <= adb_timeout:
        time.sleep(0.5)
        response = ""
        while QUEUE_ADB_OUTPUT.qsize() > 0:
            response += QUEUE_ADB_OUTPUT.get()
            last_update = time.time()
        client_socket.send(response.encode())


def start_adb_daemon():
    """Main thread to handle ADB"""
    adb_timeout = 1

    # Set daemon socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('localhost', PORT_ABD_WRITE))
    server_socket.listen(5)
    print(f"Server listening on port {PORT_ABD_WRITE}")

    with subprocess.Popen(
        ['/bin/adb', 'shell'],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE
    ) as adb_session:
        adb_session_thread = threading.Thread(
            target=output_adb_stdout,
            args=(adb_session,)
        )
        adb_session_thread.start()
        with open(PID_FILE, 'w', encoding='utf-8') as file:
            file.write(f'{adb_session.pid}\n')
            file.write(f'{os.getpid()}\n')
        print("Opened ADB session")

        while adb_session is not None:
            client_socket, _ = server_socket.accept()
            # Receive data from the client
            ready = select.select([client_socket], [], [], 0.25)
            while ready[0]:
                data = client_socket.recv(1024).decode().strip()
                ready = select.select([client_socket], [], [], 0.25)

            if len(data) > 2 and data[0:2] == "it":
                data_index = data.find("@")
                # Set timeout if possible
                try:
                    adb_timeout = float(data[2:data_index])
                except (ValueError, IndexError) as e:
                    print(f'Waring: {e} when converting timeout')
                    adb_timeout = 1
                data = data[data_index:]
            elif data[0:1] == "@":
                # Move to sending command via ADB
                pass

            # Close if received exit
            if data[1:] == "exit":
                client_socket.send("Stopping ADB\n".encode())
                client_socket.close()
                close_adb_shell(adb_session)
                return

            # Send command via ADB
            adb_session.stdin.write(f"{data[1:]}\n".encode())
            try:
                adb_session.stdin.flush()
            except BrokenPipeError:
                print('Got no reply. Is ADB device connected?')

            try:
                read_and_respond_until_timeout(client_socket, adb_timeout)
            except (ConnectionResetError, BrokenPipeError):
                pass
            client_socket.close()


# Force kill processes on signal:
def force_kill_adb_shell():
    """Kill processes in PID_FILE"""
    # Stop ADB server thread
    if os.path.exists(PID_FILE):
        with open(PID_FILE, 'r', encoding='utf-8') as file:
            for subprocess_pid in file:
                if os.name == 'posix':  # Unix/Linux
                    print(f'kill:{subprocess_pid}')
                    subprocess.run(
                        ["kill", subprocess_pid.strip()],
                        timeout=2,
                        check=False
                    )
                elif os.name == 'nt':  # Windows
                    print(f'taskkill:{subprocess_pid}')
                    subprocess.run(
                        ["taskkill", "/F", "/PID", subprocess_pid.strip()],
                        timeout=2,
                        check=False
                    )
    print('All process killed')
    try:
        os.remove(PID_FILE)
    except FileNotFoundError:
        pass


# Handling stopping process
def close_adb_shell(adb_session):
    """Close ADB peacefully"""
    # Stop output thread
    EVENT_STOP_ADB_SESSION.set()
    if adb_session is not None and adb_session.poll() is None:
        adb_session.terminate()
        try:
            adb_session.wait(timeout=1)
        except subprocess.TimeoutExpired:
            adb_session.kill()
            print('Killed adb_session')
        print('Terminated adb_session')
    try:
        os.remove(PID_FILE)
    except FileNotFoundError:
        pass


# ADB handler
def output_adb_stdout(adb_session=None):
    """Copy adb shell output to queue"""
    # Read and print all lines until timeout
    print('ABD handler started')
    while not EVENT_STOP_ADB_SESSION.is_set() and adb_session is not None:
        line = adb_session.stdout.readline().decode()
        QUEUE_ADB_OUTPUT.put(line)
    print('ABD handler stopped')

# PUBLIC API


def adb_send_via_bash():
    """Bash entry for ADB communication"""
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('text', nargs='+', help='Text to send via ADB')
    parser.add_argument(
        '-t', '--timeout', type=float,
        help='Time to wait before stop reading'
    )
    args = parser.parse_args()

    # Combine text argument into a single string
    text = ' '.join(args.text)

    # Send to ADB process stdin and read stdout
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(('localhost', PORT_ABD_WRITE))
    except ConnectionRefusedError:
        print('Did you run adb_open&')
        return

    # Set adb_timeout if necessary
    if args.timeout is not None:
        adb_timeout = args.timeout
    else:
        adb_timeout = 1

    # Send data to the daemon
    client_socket.send(f"it{adb_timeout}@{text}\n".encode())

    # Receive the response from the daemon
    ready = select.select([client_socket], [], [], adb_timeout + 1)
    while ready[0]:
        response = client_socket.recv(1024)
        if not response:
            break
        response = response.decode()
        print(response, end="")
        ready = select.select([client_socket], [], [], adb_timeout + 1)

    client_socket.close()


def adb_close():
    """Python and Shell entry for closing ADB"""
    try:
        # Send to ADB process stdin and read stdout
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', PORT_ABD_WRITE))
        # Send data to the daemon
        client_socket.send("texit".encode())
        # Receive the response from the daemon
        response = client_socket.recv(1024).decode()
        print(response)
        client_socket.close()
    except (
        InterruptedError, ConnectionResetError, ConnectionRefusedError
    ) as e:
        print(f'Warning: {e} happened when closing socket')


def adb_send(text, adb_timeout=1):
    """Python entry for ADB communication"""
    # Send to ADB process stdin and read stdout
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(('localhost', PORT_ABD_WRITE))
    except ConnectionRefusedError:
        print('Did you run adb_open()')
        return

    # Send data to the daemon
    client_socket.send(f"it{adb_timeout}@{text}\n".encode())

    # Receive the response from the daemon
    ready = select.select([client_socket], [], [], adb_timeout + 1)
    while ready[0]:
        response = client_socket.recv(1024)
        if not response:
            break
        response = response.decode()
        print(response, end="")
        ready = select.select([client_socket], [], [], adb_timeout + 1)

    client_socket.close()


def adb_open():
    """Python and Bash entry for open ADB"""
    open_adb_daemon_on_demand()


def adb_reopen():
    """Python and Bash entry for reset and open ADB"""
    force_kill_adb_shell()
    time.sleep(1)
    open_adb_daemon_on_demand()
