"""Zowe Client Python SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

import copy
import posixpath
import re
import urllib

from . import session_constants
from .logger import Log
from .request_handler import RequestHandler
from .session import ISession, Session
from typing import Any, Optional, Type

_PERCENT_ENCODED_PATTERN = re.compile(r"%[0-9A-Fa-f]{2}")

_USS_CHARS_TO_ENCODE = {" ": "%20", "%": "%25", "+": "%2B", "?": "%3F"}

# Characters that API-ML rejects with an HTTP 400 unless they are encoded.
# None of these are encoded for a direct z/OSMF connection.
_APIML_CHARS_TO_ENCODE = {
    "#": "%23",
    ";": "%3B",
    "<": "%3C",
    ">": "%3E",
    "[": "%5B",
    "]": "%5D",
    "^": "%5E",
    "{": "%7B",
    "|": "%7C",
    "}": "%7D",
}


class SdkApi:
    """
    Abstract class used to represent the base SDK API.

    Parameters
    ----------
    profile : dict[str, Any]
        Profile information in json (dict) format
    default_url : str
        Default url used for session
    logger_name : str
        Name of the logger (same as the filename by default)
    log : bool
        Flag to disable logger
    """

    def __init__(self, profile: dict[str, Any], default_url: str, logger_name: str = __name__, log: bool = True):
        session = Session(profile)
        self.session: ISession = session.load()

        self.logger = Log.register_logger(logger_name)

        if log == False:
            Log.close(self.logger)

        self._default_service_url = default_url
        self._default_headers = {
            "Content-Type": "application/json",
            "X-CSRF-ZOSMF-HEADER": "",
        }

        self._request_endpoint = session.host_url + self._default_service_url

        self._request_arguments = {
            "url": self._request_endpoint,
            "headers": self._default_headers,
        }
        self.__session_arguments: dict[str, Any] = {
            "verify": self.session.reject_unauthorized,
            "timeout": 30,
        }
        self.request_handler = RequestHandler(self.__session_arguments, logger_name=logger_name)

        if self.session.type == session_constants.AUTH_TYPE_BASIC:
            self._request_arguments["auth"] = (self.session.user, self.session.password)
        elif self.session.type == session_constants.AUTH_TYPE_BEARER:
            self._default_headers["Authorization"] = f"Bearer {self.session.token_value}"
        elif self.session.type == session_constants.AUTH_TYPE_TOKEN:
            self._default_headers["Cookie"] = f"{self.session.token_type}={self.session.token_value}"
        elif self.session.type == session_constants.AUTH_TYPE_CERT_PEM:
            cert: Optional[tuple[str, str]] = self.session.cert
            self.__session_arguments["cert"] = cert

    def __enter__(self) -> "SdkApi":
        """Return the SdkApi instance."""
        return self

    def __exit__(
        self, exc_type: Optional[Type[BaseException]], exception: Optional[BaseException], traceback: Optional[object]
    ) -> None:
        """Delete the request handler before exit."""
        del self.request_handler

    def _create_custom_request_arguments(self) -> dict[str, Any]:
        """
        Create a copy of the default request arguments dictionary.

        This method is required because the way that Python handles
        dictionary creation

        Returns
        -------
        dict[str, Any]
            A deepcopy of the request_arguments
        """
        return copy.deepcopy(self._request_arguments)

    def _encode_uri_component(self, str_to_adjust: str) -> str:
        """
        Adjust string to be correct in a URL.

        Parameters
        ----------
        str_to_adjust : str
            The string to encode

        Returns
        -------
        str
            A string with special characters, acceptable for a URL
        """
        return urllib.parse.quote(str_to_adjust, safe="!~*'()") if str_to_adjust is not None else None

    def _is_using_apiml(self) -> bool:
        """
        Determine whether requests are routed through API-ML.

        Returns
        -------
        bool
            True if the session connects through API-ML, False otherwise
        """
        if self.session.token_type == session_constants.TOKEN_TYPE_APIML:
            return True
        return self.session.base_path is not None

    def _is_uri_encoded(self, uri_path: str) -> bool:
        """
        Determine whether a path is already percent-encoded.

        A path is treated as encoded when it contains at least one percent-encoded sequence.
        A literal percent sign that is not followed by two hex digits, such as the one in the
        USS file name "100% done", is not an encoded sequence and does not make a path encoded.

        Parameters
        ----------
        uri_path : str
            The path to inspect

        Returns
        -------
        bool
            True if the path contains a percent-encoded sequence, False otherwise
        """
        return bool(_PERCENT_ENCODED_PATTERN.search(uri_path))

    def _encode_uri_path_for_zos(self, zos_uri_path: str) -> str:
        """
        Encode a z/OS resource (dataset, job, or volser) path for the path component of a URI.

        Dot-segments are resolved against the service root so a caller-supplied name such as
        "../../restjobs/jobs/OTHER" always resolves to a path under the intended resource. A
        literal "?" is always percent-encoded so a name such as "X?fsname=Y" is parsed as a
        single path value rather than a path followed by query parameters. None of the other
        documented z/OS resource naming special characters require encoding to be processed
        successfully by z/OSMF. API-ML rejects a literal "#" with an HTTP 400 error unless it is
        encoded, so it is also adjusted here when routed through API-ML.

        A path that is already percent-encoded is normalized but not encoded a second time, so
        that a caller-encoded "%23" is not turned into "%2523".

        Parameters
        ----------
        zos_uri_path : str
            The URI path to encode, either unencoded or already percent-encoded

        Returns
        -------
        str
            The normalized path, with "?" always encoded and "#" encoded when the session is
            routed through API-ML
        """
        # Normalizing against root collapses ".." segments without escaping the service path
        normalized = posixpath.normpath("/" + zos_uri_path).lstrip("/")
        if self._is_uri_encoded(normalized):
            return normalized
        encoded = normalized.replace("?", "%3F")
        if self._is_using_apiml():
            encoded = encoded.replace("#", "%23")
        return encoded

    def _encode_uri_path_for_uss(self, uss_uri_path: str) -> str:
        """
        Encode a USS file path for the path component of a URI.

        Many documented USS file name special characters cause an HTTP 500 error
        unless they are encoded. Forward slashes are preserved rather than encoded
        as %2F, since encoded slashes are expected to be rejected in future.

        A path that is already percent-encoded is normalized and validated but not encoded a
        second time, so that a caller-encoded "%20" is not turned into "%2520". A file name
        containing a literal percent sign followed by two hex digits is indistinguishable from
        an encoded path, so such a name must be passed already encoded.

        Parameters
        ----------
        uss_uri_path : str
            The USS path to encode, either unencoded or already percent-encoded

        Returns
        -------
        str
            The normalized and encoded USS path, without a leading slash

        Raises
        ------
        ValueError
            Thrown when the path contains a backslash or a double-quote character.
        """
        # Normalizing against root collapses // and resolves /../ without escaping the service path
        normalized = posixpath.normpath("/" + uss_uri_path).lstrip("/")

        if "\\" in normalized:
            # Both encoded and unencoded backslashes fail in REST requests
            self.logger.error(f"The USS path '{uss_uri_path}' contains a backslash character.")
            raise ValueError(
                f"The supplied USS path '{uss_uri_path}' contains a backslash \\ character. "
                "When a backslash is present, z/OSMF and API-ML servers fail with an HTTP 400 "
                "or 500 error code, or the backslash is ignored. This request was not sent."
            )
        if '"' in normalized:
            # Both encoded and unencoded double-quotes fail in REST requests
            self.logger.error(f"The USS path '{uss_uri_path}' contains a double-quote character.")
            raise ValueError(
                f"The supplied USS path '{uss_uri_path}' contains a double-quote \" character. "
                "When a double-quote is present, z/OSMF and API-ML servers fail with an HTTP 400 "
                "or 500 error code. This request was not sent."
            )
        if self._is_uri_encoded(normalized):
            return normalized

        encode_for_apiml = self._is_using_apiml()
        encoded_path = []
        for next_char in normalized:
            if next_char in _USS_CHARS_TO_ENCODE:
                encoded_path.append(_USS_CHARS_TO_ENCODE[next_char])
            elif encode_for_apiml and next_char in _APIML_CHARS_TO_ENCODE:
                encoded_path.append(_APIML_CHARS_TO_ENCODE[next_char])
            else:
                encoded_path.append(next_char)
        return "".join(encoded_path)
