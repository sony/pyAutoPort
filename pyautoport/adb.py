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

import argparse
import subprocess
import threading
import socket
import time
import os
import select

PORT_ABD_WRITE = 18888
PORT_ADB_SET_TIMEOUT = 18889
adb_output = ""
adb_session = None
is_stop_adb_session = False
pid_file = '/tmp/tester-adb-daemon.pid'


# Daemon
def open_adb_daemon_on_demand():
    global is_stop_adb_session
    if not os.path.exists(pid_file):
        is_stop_adb_session = False
        adb_session_thread = threading.Thread(target=start_adb_daemon)
        adb_session_thread.start()
        # TODO Fix this later
        # signal.signal(signal.SIGINT, on_signal)
    else:
        print('''
Is someone else running adb_open now?
Or did you run adb_close last time?
Run adb_reopen& instead to kill all other adb_open sessions
        ''')


def on_signal(signum, frame):
    force_kill_adb_shell()


def read_and_respond_until_timeout(client_socket, adb_timeout=1):
    global adb_output

    last_update = time.time()

    while time.time() - last_update <= adb_timeout:
        time.sleep(0.5)
        if adb_output:
            response = adb_output
            adb_output = adb_output[len(response):]
            last_update = time.time()
            client_socket.send(response.encode())


def start_adb_daemon():
    global adb_session
    global adb_output
    adb_timeout = 1

    # Set daemon socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('localhost', PORT_ABD_WRITE))
    server_socket.listen(5)
    print(f"Server listening on port {PORT_ABD_WRITE}")

    adb_session = subprocess.Popen(
        ['/bin/adb', 'shell'],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE
    )
    adb_session_thread = threading.Thread(target=output_adb_stdout)
    adb_session_thread.start()
    with open(pid_file, 'w') as file:
        file.write(f'{adb_session.pid}\n')
        file.write(f'{os.getpid()}\n')
    print("Opened ADB session")
    while adb_session is not None:
        client_socket, address = server_socket.accept()
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
            except ValueError or IndexError as e:
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
            close_adb_shell()
            return

        # Send command via ADB
        adb_session.stdin.write(f"{data[1:]}\n".encode())
        try:
            adb_session.stdin.flush()
        except BrokenPipeError:
            print('Got no reply. Is ADB device connected?')

        try:
            read_and_respond_until_timeout(client_socket, adb_timeout)
        except ConnectionResetError or BrokenPipeError:
            pass
        client_socket.close()


# Force kill processes on signal:
def force_kill_adb_shell():
    # Stop ADB server thread
    if os.path.exists(pid_file):
        with open(pid_file, 'r') as file:
            for subprocess_pid in file:
                if os.name == 'posix':  # Unix/Linux
                    print(f'kill:{subprocess_pid}')
                    subprocess.run(
                        ["kill", subprocess_pid.strip()],
                        timeout=2
                    )
                elif os.name == 'nt':  # Windows
                    print(f'taskkill:{subprocess_pid}')
                    subprocess.run(
                        ["taskkill", "/F", "/PID", subprocess_pid.strip()],
                        timeout=2
                    )
    print('All process killed')
    try:
        os.remove(pid_file)
    except FileNotFoundError:
        pass


# Handling stopping process
def close_adb_shell():
    global adb_session
    global is_stop_adb_session

    # Stop output thread
    is_stop_adb_session = True
    if adb_session is not None and adb_session.poll() is None:
        adb_session.terminate()
        try:
            adb_session.wait(timeout=1)
        except subprocess.TimeoutExpired:
            adb_session.kill()
            print('Killed adb_session')
        print('Terminated adb_session')
    adb_session = None
    try:
        os.remove(pid_file)
    except FileNotFoundError:
        pass


# ADB handler
def output_adb_stdout():
    global adb_output
    global adb_session
    global is_stop_adb_session
    # Read and print all lines until timeout
    print('ABD handler started')
    while not is_stop_adb_session and adb_session is not None:
        line = adb_session.stdout.readline().decode()
        adb_output += line
    print('ABD handler stopped')

# PUBLIC API


def adb_send_via_bash():
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
        else:
            response = response.decode()
        print(response, end="")
        ready = select.select([client_socket], [], [], adb_timeout + 1)

    client_socket.close()


def adb_close():
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
    close_adb_shell()


def adb_send(text, adb_timeout=1):
    global adb_session

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
        else:
            response = response.decode()
        print(response, end="")
        ready = select.select([client_socket], [], [], adb_timeout + 1)

    client_socket.close()


def adb_open():
    open_adb_daemon_on_demand()


def adb_reopen():
    force_kill_adb_shell()
    time.sleep(1)
    open_adb_daemon_on_demand()
