'''
Copyright 2020 Guilherme Cartier de Palma

Licensed under the Apache License, Version 2.0 (the "License"); 
you may not use this file except in compliance with the License. 
You may obtain a copy of the License at 
http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software 
distributed under the License is distributed on an "AS IS" BASIS, 
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. 
See the License for the specific language governing permissions and 
limitations under the License. 
'''

from .utilities import ZosmfConnection
from .console import Console
from .zosmf import Zosmf
from .jobs import Jobs
from .tso import Tso
class Zeepy:

    def __init__(self, zosmf_host, zosmf_user, zosmf_password, ssl_verification=True):
        self.connection = ZosmfConnection(zosmf_host,zosmf_user,zosmf_password,ssl_verification)
        self.console = Console(self.connection)
        self.zosmf = Zosmf(self.connection)
        self.jobs = Jobs(self.connection)
        self.tso = Tso(self.connection)


