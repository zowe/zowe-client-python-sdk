'''
This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zeepy project.
'''


class InvalidRequestMethod(Exception):

    def __init__(self, input_method: str):
        super().__init__("Invalid HTTP method input {}".format(input_method))


class UnexpectedStatus(Exception):

    def __init__(self, expected, received, request_output):
        super().__init__("The status code from z/OSMF was {} it was expected {}. \n {}".format(received, expected, request_output))


class RequestFailed(Exception):

    def __init__(self, status_code, request_output):
        super().__init__("HTTP Request has failed with status code {}. \n {}".format(status_code, request_output))
