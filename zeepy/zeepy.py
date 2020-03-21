"""
This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zeepy project.
"""

from .console import Console
from .files import Files
from .jobs import Jobs
from .tso import Tso
from .utilities import MissingConnectionArgs, ZosmfConnection, ZosmfProfile
from .zosmf import Zosmf


class Zeepy:
    """Main class for Zeepy"""

    def __init__(
        self,
        zosmf_host=None,
        zosmf_user=None,
        zosmf_password=None,
        ssl_verification=True,
        zosmf_profile=None,
    ):
        if zosmf_profile:
            self.connection = ZosmfProfile(zosmf_profile).load()
        else:
            if not zosmf_host or not zosmf_user or not zosmf_password:
                raise MissingConnectionArgs()

            self.connection = ZosmfConnection(
                zosmf_host=zosmf_host,
                zosmf_user=zosmf_user,
                zosmf_password=zosmf_password,
                ssl_verification=ssl_verification,
            )

        self.console = Console(self.connection)
        self.zosmf = Zosmf(self.connection)
        self.jobs = Jobs(self.connection)
        self.tso = Tso(self.connection)
        self.files = Files(self.connection)
