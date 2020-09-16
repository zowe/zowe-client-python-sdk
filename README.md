# Zowe Python Client SDK

![](https://img.shields.io/badge/license-EPL--2.0-blue) ![](https://img.shields.io/badge/dynamic/json?color=informational&label=version&query=info.version&url=https%3A%2F%2Fpypi.org%2Fpypi%2Fzowe%2Fjson) [![Documentation Status](https://readthedocs.org/projects/zowe-client-python-sdk/badge/?version=latest)](https://zowe-client-python-sdk.readthedocs.io/en/latest/?badge=latest)

The Zowe Client Python SDK, is a set of Python packages designed to allow programmatic 
interactions with z/OS REST API interfaces with minimum effort.

Python developers can leverage the Zowe SDK in order to create powerful scripts/applications
that can interact with z/OS components.

![](./img/zowesdk.gif)

## Installation


When installing the Zowe Client Python SDK you have two options.

- Install all the Zowe packages
- Install a single sub-package

The choice depends on your intentions. If you chose to install all Zowe SDK packages
this means that you will install everything under the `zowe` namespace in PyPi. 

Alternatively, you can choose to install only a single subpackage for a smaller installation.

To install all Zowe SDK packages using pip:

```
pip install zowe
```

To install only a subpackage using pip:


```
pip install zowe.<subpackage>_for_zowe_sdk
```

For more information on the available sub-packages click [HERE](https://zowe-client-python-sdk.readthedocs.io/en/latest/packages/packages.html)

## Requirements

The Zowe core package has dependencies on the below packages: 

```
requests>=2.22
keyring
pyyaml
urllib3
```


## Quickstart


After you install the package in your project, import the class for the required sub-package (i.e `Console` class for z/OS Console commands). 
Create a dictionary to handle communication with the plug-in:


```python
    from zowe.zos_console_for_zowe_sdk import Console
    connection = {
        "host_url": "'<host address>'",
        "user": "<user>",
        "password": "<password>",
    }

    my_console = Console(connection)
```

Alternatively, you can use an existing Zowe CLI profile instead:

```python
    from zowe.zos_console_for_zowe_sdk import Console

    connection = {
        "plugin_profile": "<profile name>>"
    }

    my_console = Console(connection)
```

**Important**: If your z/OSMF profile uses a credentials manager, this approach may not work depending on your operating system. Support for loading secure profiles has only been tested on Windows and Ubuntu so far.


# Available options

Currently, the Zowe Python SDK supports the following interfaces:

* Console commands
* z/OSMF Information retrieval
* Submit job from a dataset
* Submit job from local file
* Submit job as plain text JCL
* Retrieve job status
* Retrieve job list from JES spool
* Start/End TSO address space
* Ping TSO address space
* Issue TSO command

**Important**: Notice that the below examples assume that you have already created 
an object for the sub-package of your preference just like in the quickstart example.

## Console

Usage of the console api:
```python
result = my_console.issue_command("<command>")
```
The result will be a JSON object containing the result from the console command.

## Job

To retrieve the status of a job on JES
```python
result = my_jobs.get_job_status("<jobname>", "<jobid>")
```

To retrieve list of jobs in JES spool
```python
result = my_jobs.list_jobs(owner="<user>", prefix="<job-prefix>")
```
Additional parameters available are:

* max_jobs
* user_correlator

To submit a job from a dataset:
```python
result = my_jobs.submit_from_mainframe("<dataset-name>")
```

To submit a job from a local file:
```python
result = my_jobs.submit_from_local_file("<file-path>")
```

To submit from plain text:
```python
jcl = '''
//IEFBR14Q JOB (AUTOMATION),CLASS=A,MSGCLASS=0,
//             MSGLEVEL=(1,1),REGION=0M,NOTIFY=&SYSUID
//STEP1    EXEC PGM=IEFBR14
'''

result = my_jobs.submit_from_plaintext(jcl)

```

## TSO

Starting a TSO address space
```python

session_parameters = {
     'proc': 'IZUFPROC',
     'chset': '697',
     'cpage': '1047',
     'rows': '204',
     'cols': '160',
     'rsize': '4096',
     'acct': 'DEFAULT'
}

session_key = my_tso.start_tso_session(**session_parameters)
```
If you don't provide any session parameter ZoweSDK will attempt to start a session with default parameters.

To end a TSO address space
```python
my_tso.end_tso_session("<session-key>")
```

In order to issue a TSO command
```python
tso_output  =  my_tso.issue_command("<tso-command>")
```

## z/OSMF
Usage of the z/OSMF api
```python
result = my_zosmf.get_info()
```
The result will be a JSON object containing z/OSMF information


# Acknowledgments

* Make sure to check out the [Zowe project](https://github.com/zowe)!
* For further information on z/OSMF REST API, click [HERE](https://www.ibm.com/support/knowledgecenter/SSLTBW_2.1.0/com.ibm.zos.v2r1.izua700/IZUHPINFO_RESTServices.htm)