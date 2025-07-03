import unittest
from unittest.mock import patch, MagicMock
import pyautoport.uart as uart  # Assuming the original script is saved as uart.py

import os

class TestUARTBasicMode(unittest.TestCase):

    @patch('pyautoport.uart.serial.Serial')
    def test_write_and_read_uart_success(self, mock_serial_class):
        # Create a mock serial instance
        mock_serial_instance = MagicMock()
        mock_serial_class.return_value = mock_serial_instance

        # Simulate readline returning a few lines and then empty (to break loop)
        mock_serial_instance.readline.side_effect = [
            b'Hello World\n',
            b'Testing UART\n',
            b''  # End of input
        ]

        # Call the function with test values
        read_data = uart.write_and_read_uart("Test Message", uart_timeout=1, port='COM1', baudrate='9600')

        # Check if Serial object was created with correct arguments
        mock_serial_class.assert_called_with(port='COM1', baudrate=9600, timeout=1)

        # Check if write was called
        self.assertTrue(mock_serial_instance.write.called)
        written_data = [call_args[0][0] for call_args in mock_serial_instance.write.call_args_list]
        self.assertIn(b'T', written_data)  # First letter of "Test Message"

        # Check if close was called
        mock_serial_instance.close.assert_called_once()

        print(read_data)
        self.assertEqual(read_data, 'Hello World\nTesting UART\n')


    @patch('pyautoport.uart.serial.Serial')
    def test_write_and_read_uart_binary_garbage(self, mock_serial_class):
        mock_uart = MagicMock()
        mock_serial_class.return_value = mock_uart

        # Simulate binary garbage followed by normal line
        mock_uart.readline.side_effect = [
            b'\xff\xfe\xfa',
            b'Clean line\n',
            b''
        ]

        # No exceptions should occur on decoding
        uart.write_and_read_uart("Ping", uart_timeout=0.1, port='COM2', baudrate='4800')

        # Ensure write called
        self.assertGreater(mock_uart.write.call_count, 0)
        self.assertEqual(mock_uart.readline.call_count, 3)
        mock_uart.close.assert_called_once()

    @patch('pyautoport.uart.serial.Serial')
    def test_uart_port_env_default(self, mock_serial_class):
        # Remove env vars if present
        if 'TESTER_UART_PORT' in os.environ:
            del os.environ['TESTER_UART_PORT']
        if 'TESTER_UART_BAUDRATE' in os.environ:
            del os.environ['TESTER_UART_BAUDRATE']

        mock_serial_instance = MagicMock()
        mock_serial_class.return_value = mock_serial_instance
        mock_serial_instance.readline.return_value = b''

        uart.write_and_read_uart("Check Env", uart_timeout=0.1)

        mock_serial_class.assert_called_with(
            port="/dev/ttyUSB0",
            baudrate=115200,
            timeout=0.1
        )

    def test_get_default_port_from_env(self):
        os.environ['TESTER_UART_PORT'] = 'COM5'
        self.assertEqual(uart.get_default_port(), 'COM5')
        os.environ['TESTER_UART_PORT'] = 'COM1'
        self.assertEqual(uart.get_default_port(), 'COM1')

    def test_get_default_baudrate_from_env(self):
        os.environ['TESTER_UART_BAUDRATE'] = '57600'
        self.assertEqual(uart.get_default_baudrate(), '57600')
        os.environ['TESTER_UART_BAUDRATE'] = '9600'
        self.assertEqual(uart.get_default_baudrate(), '9600')

if __name__ == '__main__':
    unittest.main()
