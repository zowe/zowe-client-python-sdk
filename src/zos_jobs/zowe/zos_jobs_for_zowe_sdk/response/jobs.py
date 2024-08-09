"""Zowe Python Client SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class JobResponse:
    owner: Optional[str] = None
    phase: Optional[int] = None
    subsystem: Optional[str] = None
    phase_name: Optional[str] = None
    job_correlator: Optional[str] = None
    type: Optional[str] = None
    url: Optional[str] = None
    jobid: Optional[str] = None
    job_class: Optional[str] = None
    files_url: Optional[str] = None
    jobname: Optional[str] = None
    status: Optional[str] = None
    retcode: Optional[str] = None

    def __init__(self, response: dict) -> None:
        for k, value in response.items():
            key = k.replace("-", "_")
            if key == "class":
                key = "job_class"
            super().__setattr__(key, value)

    def __getitem__(self, key: str) -> Any:
        if key == "class":
            key = "job_class"
        return self.__dict__[key.replace("-", "_")]

    def __setitem__(self, key: str, value: Any) -> None:
        if key == "class":
            key = "job_class"
        self.__dict__[key.replace("-", "_")] = value


@dataclass
class StatusResponse:
    owner: Optional[str] = None
    jobid: Optional[str] = None
    job_correlator: Optional[str] = None
    message: Optional[str] = None
    original_jobid: Optional[str] = None
    jobname: Optional[str] = None
    status: Optional[int] = None

    def __init__(self, response: dict) -> None:
        for k, value in response.items():
            key = k.replace("-", "_")
            super().__setattr__(key, value)

    def __getitem__(self, key: str) -> Any:
        return self.__dict__[key.replace("-", "_")]

    def __setitem__(self, key: str, value: Any) -> None:
        self.__dict__[key.replace("-", "_")] = value


@dataclass
class SpoolResponse:
    recfm: Optional[str] = None
    records_url: Optional[str] = None
    stepname: Optional[str] = None
    subsystem: Optional[str] = None
    job_correlator: Optional[str] = None
    byte_count: Optional[int] = None
    lrecl: Optional[int] = None
    jobid: Optional[str] = None
    ddname: Optional[str] = None
    id: Optional[int] = None
    record_count: Optional[int] = None
    job_class: Optional[str] = None
    jobname: Optional[str] = None
    procstep: Optional[str] = None

    def __init__(self, response: dict) -> None:
        for k, value in response.items():
            key = k.replace("-", "_")
            if key == "class":
                key = "job_class"
            super().__setattr__(key, value)

    def __getitem__(self, key: str) -> Any:
        if key == "class":
            key = "job_class"
        return self.__dict__[key.replace("-", "_")]

    def __setitem__(self, key: str, value: Any) -> None:
        if key == "class":
            key = "job_class"
        self.__dict__[key.replace("-", "_")] = value
