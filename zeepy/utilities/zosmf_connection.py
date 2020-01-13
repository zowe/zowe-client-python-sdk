'''
This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zeepy project.
'''


class ZosmfConnection:

    def __init__(self, zosmf_host: str, zosmf_user: str, zosmf_password: str, ssl_verification: bool):
        self.zosmf_host = zosmf_host
        self.zosmf_user = zosmf_user
        self.zosmf_password = zosmf_password
        self.ssl_verification = ssl_verification
