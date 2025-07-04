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
Setup Script
"""

import sys
from pathlib import Path
from setuptools import setup, find_packages

with open('requirements.txt', encoding=sys.getfilesystemencoding()) as f:
    requirements = f.read().splitlines()

# read the contents of your README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='pyAutoPort',
    version='1.3.1',
    author='Yu GU',
    author_email='yu.gu@sony.com',
    description="""
    A tool automating UART and ADB interaction
    """,
    license='BSD-3-Clause',
    project_urls={
        "Homepage": "https://github.com/sony/pyAutoPort",
        "Issues": "https://github.com/sony/pyAutoPort/issues"
    },
    python_requires='>=3.8',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    packages=find_packages(),
    install_requires=requirements,
    long_description=long_description,
    long_description_content_type='text/markdown',
    entry_points={
        'console_scripts': [
            'uart_send = pyautoport.uart:uart_send',
            'adb_send = pyautoport.adb:adb_send_via_bash',
            'adb_open = pyautoport.adb:adb_open',
            'adb_reopen = pyautoport.adb:adb_reopen',
            'adb_close = pyautoport.adb:adb_close',
            'session_start = pyautoport.teraterm:open_session_start',
            'getenv = pyautoport.teraterm:get_env_via_bash',
            'setenv = pyautoport.teraterm:set_env_via_bash',
            'connect = pyautoport.teraterm:connect_via_bash',
            'send = pyautoport.teraterm:send_via_bash',
            'mpause = pyautoport.teraterm:set_pause_via_bash',
            'logstart = pyautoport.teraterm:start_log_via_bash',
            'logwrite = pyautoport.teraterm:send_log_via_bash',
            'logstop = pyautoport.teraterm:stop_log_via_bash',
            'set_timestamp = pyautoport.teraterm:set_timestamp_via_bash',
            'set_timeout = pyautoport.teraterm:set_timeout_via_bash',
            'waitln = pyautoport.teraterm:wait_log_via_bash',
            'disconnect = pyautoport.teraterm:disconnect_via_bash',
            'session_stop = pyautoport.teraterm:session_stop',
        ],
    },
)
