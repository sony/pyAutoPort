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
TeraTerm Mode - abstractmethod
"""

from abc import ABC, abstractmethod

class AddonStrategy(ABC):
    """ abstractmethod for session """
    _instance = None
    _first_init = True
    timestamp = False

    @abstractmethod
    def set_timeout(self, timeout):
        """ abstractmentod for set timeout """

    @abstractmethod
    def set_log(self, log_file, save_flag):
        """ abstractmentod for set logstart/logstop """

    @abstractmethod
    def connect(self):
        """ abstractmentod for connect """

    @abstractmethod
    def send_data(self, data):
        """ abstractmentod for send command """

    @abstractmethod
    def send_data_to_log(self, data):
        """ abstractmentod for send date to logfile """

    @abstractmethod
    def read_data(self, data):
        """ abstractmentod for read data """

    @abstractmethod
    def disconnect(self):
        """ abstractmentod for disconnect """
