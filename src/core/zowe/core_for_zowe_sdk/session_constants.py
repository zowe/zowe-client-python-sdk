"""Zowe Python Client SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

# Session type property value for no authentication
AUTH_TYPE_NONE = "none"


# Session type property value for basic authentication
AUTH_TYPE_BASIC = "basic"


# Session type property value for bearer token authentication
AUTH_TYPE_BEARER = "bearer"


# Session type property value for cookie token authentication,
# which uses a named token type.
AUTH_TYPE_TOKEN = "token"


# Session type property value for certificate authentication,
# which uses a certificate file and key file.
AUTH_TYPE_CERT_PEM = "cert-pem"


# https protocol defaults
DEFAULT_HTTPS_PORT = 443
HTTPS_PROTOCOL = "https"
