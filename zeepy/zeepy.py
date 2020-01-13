'''
This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zeepy project.
'''

from .utilities import ZosmfConnection
from .console import Console
from .zosmf import Zosmf
from .jobs import Jobs
from .tso import Tso
from .files import Files


class Zeepy:

    def __init__(self, zosmf_host: str, zosmf_user: str, zosmf_password: str, ssl_verification: bool = True):
        self.connection = ZosmfConnection(zosmf_host, zosmf_user, zosmf_password, ssl_verification)
        self.console = Console(self.connection)
        self.zosmf = Zosmf(self.connection)
        self.jobs = Jobs(self.connection)
        self.tso = Tso(self.connection)
        self.files = Files(self.connections)
