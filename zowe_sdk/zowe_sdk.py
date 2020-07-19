"""Zowe Python Client SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

from .console import Console
from .files import Files
from .jobs import Jobs
from .tso import Tso
from .utilities import MissingConnectionArgs, ZosmfConnection, ZosmfProfile
from .zosmf import Zosmf


class ZoweSDK:
    """
    Main class for Zowe Python Client SDK.

    ...

    Attributes
    ----------
    zosmf_host: str
        zosmf host address
    zosmf_user: str
        zosmf rest api user
    zosmf_password: str
        zosmf rest api password
    ssl_verification: bool
        request ssl verification parameter (default True)
    zosmf_profile: str
        zosmf profile name to be loaded (default None)
    connection
        zosmf connection object
    console
        z/osmf console base api
    zosmf
        z/osmf base api
    jobs
        z/osmf jobs base api
    tso
        z/osmf tso base api
    files
        z/osmf files base api
    """

    def __init__(
        self,
        zosmf_host=None,
        zosmf_user=None,
        zosmf_password=None,
        ssl_verification=True,
        zosmf_profile=None,
    ):
        """
        Construct a ZoweSDK object.

        Parameters
        ----------
        zosmf_host
            The z/OSMF host address (default is None)
        zosmf_user
            The user for the z/OSMF REST API (default is None)
        zosmf_password
            The password for the z/OSMF REST API (default is None)
        ssl_verification
            The value for the requests ssl verification parameter (default is True)
        zosmf_profile
            The Zowe z/OSMF profile name in case it already exists (default is None)

        Raises
        ------
        MissingConnectionArgs
            If no connection argument is passed (In-line connection or Zowe z/OSMF profile)
        """
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
