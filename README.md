# Zeepy

![](https://img.shields.io/hexpm/l/plug) 

Zeepy is an open-source Python library for z/OSMF REST API. It allows you to leverage mainframe capabilities from your python programs with minimum effort!

![](./img/zeepy.gif)

# Requirements

This library uses `requests-2.22`

# Quick start

Start by importing the Zeepy class and create a object that will be the handler for all z/OSMF requests:

```python
from zeepy import Zeepy

z = Zeepy(zosmf_host='<host address>', zosmf_user='<zosmf user>', zosmf_password='<zosmf password>')
```

# Available options

Currently the avaiable interfaces are

1. Issue console command:
```python
result = z.console.issue_command("<command>")
```

2. Retrieve z/OSMF information
```python
result = z.zosmf.get_info()
```

3. Retrieve the status of a job on JES
```python
result = z.jobs.get_job_status("JOBNAME", "JOBID")
```

4. Retrieve list of jobs in JES spool
```python
result = z.jobs.list_jobs(owner="USER", prefix="JOB*")
```

5. Submit a job from a dataset:
```python
result = z.jobs.submit_from_mainframe("YOUR.DATASET")
```

6. Submit a job from a local file:
```python
result = z.jobs.submit_from_local_file("./local_file")
```

7. Submit from plain text:
```python
jcl = '''
//IEFBR14Q JOB (AUTOMATION),CLASS=A,MSGCLASS=0,
//             MSGLEVEL=(1,1),REGION=0M,NOTIFY=&SYSUID
//STEP1    EXEC PGM=IEFBR14
'''

result = z.jobs.submit_from_plaintext(jcl)

```

# Acknowledgments 

* Make sure to check out the [Zowe project](https://github.com/zowe)! 
* For further information on z/OSMF REST API, click [HERE](https://www.ibm.com/support/knowledgecenter/SSLTBW_2.1.0/com.ibm.zos.v2r1.izua700/IZUHPINFO_RESTServices.htm)
