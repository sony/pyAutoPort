# Quick Start

pyAutoPort is a collection of BASH/ZSH tools that makes it easier and more consistent to communicate with a Device Under Test (DUT) connected via UART or ADB. It's built for embedded system engineers to automate testing.

These commands can be executed directly from the terminal as system commands.

pyAutoPort also provides Python APIs that automatically handles opening and closing the UART connection, incorporates a defined timeout for reading responses, and gracefully handles potential decoding errors by including undecodable data in hexadecimal format.

## Installation

Install pyAutoPort-related commands using:

```bash
pip install pyAutoPort
```

Run this command INSIDE JUPYTER if you want to use this in a Jupyter notebook or Jupyter Lab.

## Set Configuration

To specify the UART port and baudrate or ADB Serial Number, define them in environment variables like this:

- Linux/MacOS

```bash
export TESTER_UART_PORT="/dev/ttyACM0"
export TESTER_UART_BAUDRATE=1250000
export TESTER_ADB_PORT=Serial_number
```
- Windows Command Prompt

```bash
set TESTER_UART_PORT="COM0"
set TESTER_UART_BAUDRATE=1250000
set TESTER_ADB_PORT=Serial_number
```
- Windows PowerShell

```bash
$Env:TESTER_UART_PORT = 'COM0'
$Env:TESTER_UART_BAUDRATE = 1250000
$Env:TESTER_ADB_PORT = Serial_number
```

> `adb devices -l` can get `Serial_number`. Default `adb shell` if `TESTER_ADB_PORT` not been setted.

## Sending UART Commands

### Calling from Command Line

Send UART commands and receive replies with:

```bash
uart_send ${MESSAGE}
```

For example, you should be able to see "connected" in the output after running:

```bash
uart_send "echo connected"
```

You don't need to send other commands to get output; `uart_send` will return the output.

For additional information, refer to the [Basic Mode](#basic-mode) section.

### Calling from Python

The `write_and_read_uart` function allows you to send text to a UART interface and retrieve any response received until a specified timeout occurs.

**Function Signature:**

```python
def write_and_read_uart(text, uart_timeout, port=None, baudrate=None):
    """Writes text to the UART and reads all available lines until a timeout.

    Args:
        text: The text to write to the UART.
        uart_timeout: The timeout for UART operations (in seconds).
        port: The UART port to use (e.g., '/dev/ttyUSB0'). If None, the default port is used.
        baudrate: The baudrate to use (e.g., 115200). If None, the default baudrate is used.

    Returns:
        A string containing the reply received from the UART.  If any received data could not be decoded as UTF-8, its hexadecimal representation is included in the returned string.
    """
```

**Basic Usage:**

To send a simple command and retrieve the response, you can use the following:

```python
response = write_and_read_uart("AT+INFO\n", 2.0)  # Sends "AT+INFO\n" and waits up to 2 seconds for a response.
print(response)
```

**Specifying Port and Baudrate:**

If your UART interface isn't using the default port or baudrate, you can specify them explicitly:

```python
response = write_and_read_uart("AT+VERSION\n", 1.5, port="/dev/ttyACM0", baudrate=9600)
print(response)
```

**Important Considerations:**

*   **Newline Characters:** The function requires a newline character (`\n`) to be appended to the `text` being sent.  The UART device typically expects this to signal the end of the command.
*   **Timeout:** The `uart_timeout` parameter is crucial. Set it long enough for the device to complete its operation and send a reply, but not so long that the program waits unnecessarily.
*   **Decoding Errors:**  If the UART device sends data that cannot be decoded using UTF-8, the undecodable portion is represented in the response string using its hexadecimal equivalent.  This helps in debugging communication issues.  You might need to investigate the device's documentation to understand the expected data format.
*   **Default Port and Baudrate:** The function uses `get_default_port()` and `get_default_baudrate()` to determine the default values if `port` and `baudrate` are not provided.  Make sure these functions are defined and configured correctly.

## Interacting with ADB

While `adb shell xxx` is widely used to run shell commands from scripts without user interaction, direct interaction via the command-line interface (CLI) is necessary sometimes, especially when running an interactive app behind ADB.

This package provides tools for keeping an ADB session open and interacting with it directly from a script without being trapped by `adb shell`.

### Open A Persistent ADB Session

```bash
adb_open&
```

### Send Commands to ADB Session

```bash
adb_send some command
adb_send another command
```

### Close ADB Sessions

```bash
adb_close
```

These commands simplify the process of sending and receiving data to and from your DUT using UART and ADB in various testing scenarios.

For additional information, refer to the [Basic Mode](#basic-mode) section.

## Interacting support TeraTerm-compatible commands

TeraTerm Mode Support TTL commands which can making automation scripting easier.

### TeraTerm Mode Start

Create a Session, Use connect command to configure the connection.

In a Session, multiple different types of connections can be connected simultaneously without affecting each other.

- Linux/MacOS

```bash
session_start&
```

- Windows

```bash
start /B session_start
```

### Send TTL commands

Following commands supported
- getenv
- setenv
- connect
- logstart
- logwrite
- logstop
- send
- mapuse
- waitln
- disconnect

For additional information, refer to the [TeraTerm Mode](#teraterm-mode) section.

### Session Stop

At the end of the session, all connections will be disconnected and the log will be saved if necessary.

```bash
session_stop
```

# Basic Mode

Basic Mode provides commands integreated into Shell or Windows Command Propmt or PowerShell. Communication on UART and ADB are wrapped as command line commands.

Basic usage of Basic Mode can be found in [Quick Start](#quick-start) section. The following part focuses on additional information.

## UART Communication

The `uart_send` command facilitates interaction with UART. Its usage is as follows:

```bash
usage: uart_send [-h] [-t TIMEOUT] text [text ...]

positional arguments:
  text                  Text to be sent via UART

options:
  -h, --help            Display this help message and exit
  -t TIMEOUT, --timeout TIMEOUT
                        Time to wait before stopping reading
```

When using `uart_send`, it will continuously print text received from UART until there is no new text within a 0.5-second interval. To extend the duration before stopping, specify a new timeout value using `-t TIMEOUT`.

**IMPORTANT:** If UART continues to print text, especially in scenarios with enabled debugging logs, you may need to press `Ctrl-C` to stop forcefully.

## ADB Communication

Unlike UART, interacting with ADB involves a three-step process: opening an ADB session, interacting within the session, and finally closing the ADB session.

To initiate an ADB session, use the commands `adb_open` or `adb_reopen`. If a previous session was not closed safely, it's recommended to use `adb_reopen` for recovery.

**IMPORTANT:** Run `adb_open&` to open the session in the background. Otherwise, using `adb_open` alone will block further command execution since it is a blocking command call.

For interaction with ADB, employ the `adb_send` command with the following usage:

```bash
usage: adb_send [-h] [-t TIMEOUT] text [text ...]

positional arguments:
  text                  Text to send via ADB

options:
  -h, --help            show this help message and exit
  -t TIMEOUT, --timeout TIMEOUT
                        Time to wait before stopping reading
```

The `adb_send` command will continuously print text received from ADB until no new text is received within a 1-second timeframe. To extend the timeout duration before stopping, use the `-t TIMEOUT` option.

**IMPORTANT:** In situations where ADB keeps printing text, such as when running logcat, you may need to press `Ctrl-C` to stop forcefully.

# TeraTerm Mode

TeraTerm Mode Support TTL commands on Linux or Windows CLI via adb or uart.

## getenv

Gets an environment variable.

```bash
getenv <envname>
```

## setenv

Sets an environment variable.

```bash
setenv <envname> <strval>
```

## connect

Start one connection or switch other connection.
If switch other connection, the existed connection will not be disconnected.

```bash
connect [uart|adb]
```

Example:
```bash
connect adb     -> ADB connection create
send xxx        -> send xxx via ADB
connect uart    -> UART connection create and switch UART
send xxx        -> send xxx via UART
connect adb     -> switch ADB
send xxx        -> send xxx via ADB
```

## logstart

Start to Saving Received Messages to specified file.
This command must be used after one connection has been already created.

```bash
logstart <filename>
```

- Add TimeStamp in log

```bash
set_timestamp
logstart <filename>
```

## logwrite

Writes a string to the log file.

```bash
logwrite <string>
```

## logstop

Stop saving logs into the log file.

```bash
logstop
```

## send

Send commands via current connection.
Received Messages will be printed on CLI.

```bash
send <date1> <date2> ...
```

## mpause

Pauses.

```bash
mpause <milliseconds>
```

## waitln

Waits a line that contains string.
Pauses until a line which contains one of the character strings is received from the host, or until the timeout occurs.

```bash
set_timeout 2
waitln <string1> [<string2> ...]
```

## disconnect

Stop specified connection.

```bash
disconnect [uart|adb]
```

Some commands will be supported in the future.

# How to Contribute

See [contributing guidelines](CONTRIBUTING.md) for details. [commit guidelines](COMMIT_GUIDELINES.md) may also be helpful.

# LICENSE

This project is under BSD-3 license.

# Credits

We express our gratitude to all contributors for their valuable contributions to pyAutoPort!

## Maintainers

- Yu GU <Yu.Gu@sony.com> (Basice Mode)
- Shuang LIANG <Shuang.Liang@sony.com> (TeraTerm Mode)

## Contributors

Happy coding!
