# Quick Start

pyAutoPort is a BASH/ZSH toolset for communicating with a Device Under Test (DUT) connected via UART and/or ADB. Embedded system engineers can use this toolset for automating tests.

These commands can be executed directly from the terminal as system commands.

## Installation

Install pyAutoPort-related commands using:

```bash
/bin/pip install .
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
- Windows

```bash
set TESTER_UART_PORT="COM0"
set TESTER_UART_BAUDRATE=1250000
set TESTER_ADB_PORT=Serial_number
```

> `adb devices -l` can get `Serial_number`. Default `adb shell` if `TESTER_ADB_PORT` not been setted.

## Interacting with specified

### Sending UART Commands

Send UART commands and receive replies with:

```bash
uart_send ${MESSAGE}
```

For example, you should be able to see "connected" in the output after running:

```bash
uart_send "echo connected"
```

You don't need to send other commands to get output; `uart_send` will return the output.

### Sending ADB Commands

While `adb shell xxx` is widely used to run shell commands from scripts without user interaction, direct interaction via the command-line interface (CLI) is necessary sometimes, especially when running an interactive app behind ADB.

This package provides tools for keeping an ADB session open and interacting with it directly from a script without being trapped by `adb shell`.

1. Open A Persistent ADB Session

```bash
adb_open&
```

2. Send Commands to ADB Session

```bash
adb_send some command
adb_send another command
```

3. Close ADB Sessions

```bash
adb_close
```

## Interacting with Customize

### Start Interaction Session

Put `adb session` and `uart session` into thread to implement non blocking interactions.
Support for saving logs with timestamp during interaction.

- Linux/MacOS

```bash
start_daemon&
```

- Windows

```bash
start /B start_daemon
```

### Connect with Specified Session

Start one specified connection session or switch other session.
Even if executed multiple or switch other session, the existing session will not be disconnected
One connection has only one session.

- uart

```bash
uart_connect
```

- adb

```bash
adb_connect
```

### Save Log

Saving Received Messages to specified file.
This command must be used after one session has been already created.

```bash
set_log filename
```

- Add TimeStamp in Received Messages

```bash
set_timestamp
```

### Send Commands

Send commands via current session.
Received Messages will be printed on interface.

```bash
send some command
send another command
```

### Disconnect with Specified Session

Stop specified connection session.

- uart

```bash
uart_disconnect
```

- adb

```bash
adb_disconnect
```

### Stop Interaction Session

Disconnect all sessions and stop interaction.

```bash
stop_daemon
```

These commands simplify the process of sending and receiving data to and from your DUT using UART and ADB in various testing scenarios.

# How to Contribute

See [contributing guidelines](CONTRIBUTING.md) for details. [commit guidelines](COMMIT_GUIDELINES.md) may also be helpful.

# LICENSE

This project is under BSD-3 license.

# Credits

We express our gratitude to all contributors for their valuable contributions to pyAutoPort!

## Maintainers

- Yu GU <Yu.Gu@sony.com>
- Shuang LIANG <Shuang.Liang@sony.com>

## Contributors

Happy coding!
