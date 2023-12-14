# Quick Start

pyAutoPort is a BASH/ZSH toolset for communicating with a Device Under Test (DUT) connected via UART and/or ADB. Embedded system engineers can use this toolset for automating tests.

These commands can be executed directly from the terminal as system commands.

## Installation

Install pyAutoPort-related commands using:

```bash
/bin/pip install .
```

Run this command INSIDE JUPYTER if you want to use this in a Jupyter notebook or Jupyter Lab.

## Sending UART Commands

Send UART commands and receive replies with:

```bash
uart_send ${MESSAGE}
```

For example, you should be able to see "connected" in the output after running:

```bash
uart_send "echo connected"
```

To specify the UART port and baudrate, define them in environment variables like this:

- Linux/MacOS

```bash
export TESTER_UART_PORT="/dev/ttyACM0"
export TESTER_UART_BAUDRATE=1250000
```
- Windows

```bash
set TESTER_UART_PORT="/dev/ttyACM0"
set TESTER_UART_BAUDRATE=1250000
```

You don't need to send other commands to get output; `uart_send` will return the output.

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
