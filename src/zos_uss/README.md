z/OS UNIX System Services (USS) Package
=======================================

Provides APIs to interact with z/OS UNIX System Services (USS) over SSH (using z/OSMF or other SSH connections).

Examples
--------

### Issue a command in the z/OS USS environment

```
from zowe.core_for_zowe_sdk import ProfileManager
from zowe.zos_uss_for_zowe_sdk import Uss

profile = ProfileManager().load(profile_name="zosmf")

with Uss(profile) as uss:
    print(uss.execute_command(command="ls -la", cwd="/u/home"))
```

### Possible Limitations
Some commands executed via SSH may change the code page (character encoding) of the remote session, leading to unexpected behavior.
This is especially relevant for z/OS USS environments, where different datasets or terminal settings may use EBCDIC (e.g., IBM-1047) instead of UTF-8.
If you encounter encoding issues, ensure that your session consistently uses UTF-8 or explicitly specify the correct encoding when reading output.

Also, the Paramiko SSH library may not always handle special characters correctly (e.g., ööö, 👍, 🔟) due to encoding mismatches. 
This can happen if:
The remote shell is using a different encoding than expected.
The Python script doesn't explicitly decode the output.
If you run into issues, try explicitly decoding stdout/stderr using the correct encoding.
Lastly, to avoid encoding problems when retrieving command output, explicitly decode the response using UTF-8 (or the appropriate encoding for your environment). 
Meanwhile, if dealing with EBCDIC-based systems (e.g., z/OS), you may need to decode using IBM-specific encodings