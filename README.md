# Zeepy

Zeepy is an open-source Python library for z/OSMF REST API. It allows you to leverage mainframe capabilities from your python programs with minimum effort!

![]("./img/zeepy.gif")

# Requirements

This library uses `requests-2.22`

# Quick start

Start by importing the Zeepy class and create a object that will be the handler for all z/OSMF requests:

```python
from zeepy import Zeepy

z = Zeepy(zosmf_host='<your zosmf host address>', zosmf_user='<your zosmf user>', zosmf_password='<your zosmf password>'
```

# Available options

1. Issue console command:
```python
result = z.console.issue_command("<command>")
```

2. Retrieve z/OSMF information
```python
result = z.zosmf.get_info()
```

3. Submit a job from a dataset:
```python
result = z.job.submit_from_mainframe("YOUR.DATASET")
```

4. Submit a job from a local file:
```python
result = z.job.submit_from_local_file("./local_file")
```

5. Submit from plain text:
```
jcl = '''
//IEFBR14Q JOB (AUTOMATION),CLASS=A,MSGCLASS=0,
//             MSGLEVEL=(1,1),REGION=0M,NOTIFY=&SYSUID
//STEP1    EXEC PGM=IEFBR14
'''

result = z.job.submit_from_plaintext(jcl)

```

