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
UART Basic Mode
"""

import argparse
import time
import os
import serial

def get_default_port():
    # Get UART parameters from environment variable
    port = os.environ.get("TESTER_UART_PORT", "/dev/ttyUSB0")
    return port

def get_default_baudrate():
    # Get UART parameters from environment variable
    baudrate = os.environ.get("TESTER_UART_BAUDRATE", "115200")
    return baudrate

def write_and_read_uart(text, uart_timeout, port=None, baudrate=None):
    """Send and receive reply"""

    if port is None:
        port = get_default_port()
    if baudrate is None:
        baudrate = get_default_baudrate()

    # Open UART connection
    uart = serial.Serial(
            port=port,
            baudrate=int(baudrate),
            timeout=uart_timeout
    )

    # Send text to UART
    for byte_to_encode in text:
        uart.write(byte_to_encode.encode('utf-8'))
        time.sleep(0.05)

    # Read and print all lines from UART until timeout
    reply = ''
    while True:
        line = uart.readline()
        if not line:
            break
        try:
            reply += f'{line.decode('utf-8').strip()}\n'
        except UnicodeDecodeError:
            reply += line.hex()

    # Close UART connection
    uart.close()
    return reply

def uart_send():
    """Python wrapper to provide consistant command name"""

    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('text', nargs='+', help='Text to send via UART')
    parser.add_argument(
        '-t', '--timeout', type=float,
        help='Time to wait before stop reading'
    )
    args = parser.parse_args()

    # Set adb_timeout if necessary
    if args.timeout is not None:
        uart_timeout = args.timeout
    else:
        uart_timeout = 0.5

    # Combine text argument into a single string
    text = ' '.join(args.text)

    # Append newline character to text
    text += '\n'

    try:
        print(write_and_read_uart(text, uart_timeout))
    except serial.serialutil.SerialException:
        print(f'''
Can\'t Open {port}. Did you set port using:
export TESTER_UART_PORT=/dev/ttyXXX (On Linux)
set TESTER_UART_PORT=COMx (For Windows CMD (Command Prompt))
$Env:TESTER_UART_PORT = 'COMx' (For Windows PowerShell)
''')
