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
TeraTerm Mode - Connect Session
"""

from pyautoport.addon.adb import ADBStrategy
from pyautoport.addon.tty import TTYStrategy

class ConnectSession():
    """ Base Class """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConnectSession, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self._type = None
        self.strategy = None

    @property
    def type(self):
        """ get session type """
        return self._type

    @type.setter
    def type(self, type_choose):
        """ set session type """
        self._type = type_choose
        if type_choose == 'tty':
            self.strategy = TTYStrategy()
        elif type_choose == 'adb':
            self.strategy = ADBStrategy()
        else:
            raise ValueError('Invalid connection type')

    def connect(self, *args, **kwargs):
        """ invoke connect """
        self.strategy.connect(*args, **kwargs)

    def connect_check(self):
        """ get connect status """
        return self.strategy.running

    def set_timeout(self, timeout):
        """ set timeout """
        self.strategy.set_timeout(timeout)

    def set_log(self, log_file):
        """ log start """
        self.strategy.set_log(log_file)

    def set_timestamp(self):
        """ set timestamp """
        self.strategy.timestamp = True

    def send_data(self, data):
        """ send data via connection """
        self.strategy.send_data(data)

    def disconnect(self):
        """ invoke disconnect """
        self.strategy.disconnect()
